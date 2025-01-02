import time
from datetime import datetime
import redis
from abc import ABC, abstractmethod
import json
import logging
import pandas as pd

# Logger Configuration
py_logger = logging.getLogger("ProductionLogger")
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler("logfile.log", mode="w")
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)


# Abstract State Base Class
class StepState(ABC):
    @abstractmethod
    def handle_event(self, step, event, start_time=None):
        pass

    @abstractmethod
    def update(self, step, current_time):
        pass

    @abstractmethod
    def render(self, step):
        pass


# State Classes
class PendingState(StepState):
    def handle_event(self, step, event, start_time=None):
        if event == "start":
            step.start_time = start_time or datetime.now()
            step.last_update_time = step.start_time
            step.state = RunningState()
            py_logger.info(f"Step {step.name} started at {step.start_time}.")

    def update(self, step, current_time):
        pass  # No updates in PENDING state

    def render(self, step):
        return f"Step {step.name}: State = PENDING"


class RunningState(StepState):
    def handle_event(self, step, event, start_time=None):
        if event == "complete":
            step.end_time = datetime.now()
            step.elapsed_time = (step.end_time - step.start_time).total_seconds()
            step.state = CompleteState()
            py_logger.info(f"Step {step.name} completed with final stats:")
            py_logger.info(step.render())

    def update(self, step, current_time):
        time_since_last_update = (current_time - step.last_update_time).total_seconds()
        step.active_time += time_since_last_update
        step.elapsed_time = (current_time - step.start_time).total_seconds()
        step.last_update_time = current_time
        
        if step.active_time < step.standard_duration:
            step.remaining_time = (step.standard_duration - step.active_time) 
        else:
            step.remaining_time = 0
        
        
        # Transition to IDLE if active_time exceeds standard_duration
        # and step is not a processing step
        if step.active_time > step.standard_duration and step.is_processing_step == 0:
            step.state = IdleState()
            step.last_idle_time_update = current_time
            py_logger.info(f"Step {step.name} is now IDLE.")
        
        # Mechanism for calculting the step performance if its a processing step
        
        if step.is_processing_step == 1:
            if step.active_time < step.standard_duration:
                # Assumes performance = 100%
                step.processing_performance = 1.0 
            else:
                # Calculates performance % based on ratio of standard time to active time
                step.processing_performance =  step.standard_duration / step.active_time
            
    def render(self, step):
        return (
            f"Step {step.name}: State = RUNNING, "
            f"Elapsed Time = {step.elapsed_time:.2f} seconds, "
            f"Idle Time = {step.idle_time:.2f} seconds, "
            f"Active Time = {step.active_time:.2f} seconds, "
            f"Remaining Time = {step.remaining_time:.2f} seconds, "
            f"Processing performance = {step.processing_performance}"
        )


class IdleState(StepState):
    def handle_event(self, step, event, start_time=None):
        if event == "resume":
            step.state = RunningState()
            step.last_update_time = datetime.now()
            py_logger.info(f"Step {step.name} resumed.")
        elif event == "complete":
            step.end_time = datetime.now()
            step.elapsed_time = (step.end_time - step.start_time).total_seconds()
            step.state = CompleteState()
            py_logger.info(f"Step {step.name} completed from IDLE state.")

    def update(self, step, current_time):
        time_since_last_update = (current_time - step.last_update_time).total_seconds()
        step.idle_time += time_since_last_update
        step.elapsed_time = (current_time - step.start_time).total_seconds()
        step.last_update_time = current_time

    def render(self, step):
        return (
            f"Step {step.name}: State = IDLE, "
            f"Elapsed Time = {step.elapsed_time:.2f} seconds, "
            f"Idle Time = {step.idle_time:.2f} seconds"
        )


class CompleteState(StepState):
    def handle_event(self, step, event, start_time=None):
        pass  # No events in COMPLETE state

    def update(self, step, current_time):
        pass  # No updates in COMPLETE state

    def render(self, step):
        return (
            f"Step {step.name}: State = COMPLETE, "
            f"Elapsed Time = {step.elapsed_time:.2f} seconds"
        )


# Step Class
class Step:
    def __init__(self, name, standard_duration, is_processing_step=0):
        self.name = name
        self.standard_duration = standard_duration
        self.is_processing_step = is_processing_step
        self.processing_performance = 1.0  # Default 100%
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0
        self.idle_time = 0
        self.active_time = 0
        self.remaining_time = 0
        self.state = PendingState()
        self.last_update_time = None

    def handle_event(self, event, start_time=None):
        self.state.handle_event(self, event, start_time)

    def update(self, current_time):
    if self.state in [CompleteState(), IdleState()]:
        return  # Skip update if the step is complete or idle

    self.state.update(self, current_time)
    def render(self):
        return self.state.render(self)


# Step Sequence
class Sequence:
    def __init__(self, steps):
        self.steps = steps
        self.current_step_index = 0

    def start_next_step(self, step_name, start_time):
    step_index = next(
        (i for i, step in enumerate(self.steps) if step.name == step_name), None
    )

    if step_index is None:
        py_logger.warning(f"Step {step_name} not found in sequence.")
        return

    if step_index < self.current_step_index:
        py_logger.warning(f"Step {step_name} is already completed.")
        return

    for i in range(self.current_step_index, step_index):
        skipped_step = self.steps[i]
        if not isinstance(skipped_step.state, CompleteState):
            py_logger.info(f"Skipping step {skipped_step.name}. Marking as complete.")
            skipped_step.handle_event("complete")

    if self.current_step_index < len(self.steps):
        # Calculate elapsed times retrospectively for the current step
        current_step = self.steps[self.current_step_index]
        if not isinstance(current_step.state, CompleteState):
            current_step.elapsed_time = (start_time - current_step.start_time).total_seconds()
            current_step.active_time = current_step.elapsed_time - current_step.idle_time
            current_step.remaining_time = max(0, current_step.standard_duration - current_step.active_time)

    # Start the next step
    current_step = self.steps[step_index]
    current_step.handle_event("start", start_time)
    self.current_step_index = step_index
    
    def update(self, current_time):
        if self.current_step_index < len(self.steps):
            self.steps[self.current_step_index].update(current_time)

    def render(self):
        for step in self.steps:
            print(step.render())


# Production Engine
class ProductionEngine:
    """ Production Engine """
    def __init__(self, step_sequence):
        self.redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.step_sequence = step_sequence
        self.messages = []
        self.frame = 0

    def process_input(self):
        while self.redis_client.llen("operation_queue") > 0:
            json_str = self.redis_client.rpop("operation_queue")
            record = json.loads(json_str)
            step_name = record["step"]
            start_time = datetime.strptime(record["start_time"], "%Y-%m-%d %H:%M:%S")
            self.messages.append((step_name, start_time))

    def update(self):
        current_time = datetime.utcnow()
        self.step_sequence.update(current_time)

        while self.messages:
            step_name, start_time = self.messages.pop(0)
            self.step_sequence.start_next_step(step_name, start_time)

    def render(self):
        print(f"Frame {self.frame + 1}")
        self.step_sequence.render()
        print("-" * 30)

    def run(self):
        """Production Loop """
        # 1. Process input data
        self.process_input()
        
        # 2. Update 
        self.update()
        
        # 3. Render
        self.render()
        
        time.sleep(2)
        self.frame += 1


# Load Steps
df = pd.read_csv("batch_routing.csv")
steps = [Step(row["step"], row["duration"]) for _, row in df.iterrows()]
step_sequence = Sequence(steps)

# Start Production
engine = ProductionEngine(step_sequence)
while True:
    engine.run()