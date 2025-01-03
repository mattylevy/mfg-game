import time
from datetime import datetime
import redis
from abc import ABC, abstractmethod
import json

import logging
import pandas as pd
# get a custom logger & set the logging level
py_logger = logging.getLogger("logfile")
py_logger.setLevel(logging.INFO)

# configure the handler and formatter as needed
py_handler = logging.FileHandler("logfile.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# add formatter to the handler
py_handler.setFormatter(py_formatter)
# add handler to the logger
py_logger.addHandler(py_handler)






# Abstract State Base Class
class StepState(ABC):
    @abstractmethod
    def handle_event(self, step, event):
        pass

    @abstractmethod
    def update(self, step, current_time):
        pass

    @abstractmethod
    def render(self, step):
        pass


# State Classes
class PendingState(StepState):
    def handle_event(self, step, event):
        if event == "start":
            step.start_time = datetime.now()
            step.state = RunningState()
            step.last_update_time = step.start_time
            py_logger.info(f"Step {step.name} started.")

    def update(self, step, current_time):
        pass  # No updates in PENDING state

    def render(self, step):
        return f"Step {step.name}: State = PENDING"


class RunningState(StepState):
    def handle_event(self, step, event):
        if event == "complete":
            step.end_time = datetime.now()
            step.elapsed_time = (step.end_time - step.start_time).total_seconds()
            step.state = CompleteState()
            py_logger.info(f"Step {step.name} completed. Finalized attributes:")
            py_logger.info(step.render())

    def update(self, step, current_time):
        step.active_time += (current_time - step.last_update_time).total_seconds()
        step.elapsed_time += (current_time - step.last_update_time).total_seconds()
        step.last_update_time = current_time

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
            f"Processing performance = {step.processing_performance}"
        )


class IdleState(StepState):
    def handle_event(self, step, event):
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
        step.idle_time += (current_time - step.last_idle_time_update).total_seconds()
        step.elapsed_time += (current_time - step.last_update_time).total_seconds()
        step.last_idle_time_update = current_time

    def render(self, step):
        return (
            f"Step {step.name}: State = IDLE, "
            f"Elapsed Time = {step.elapsed_time:.2f} seconds, "
            f"Idle Time = {step.idle_time:.2f} seconds, "
            f"Active Time = {step.active_time:.2f} seconds, "
            f"Processing performance = {step.processing_performance}"
        )
        


class CompleteState(StepState):
    def handle_event(self, step, event):
        pass  # No events are processed in COMPLETE state

    def update(self, step, current_time):
        pass  # No updates in COMPLETE state

    def render(self, step):
        return (
            f"Step {step.name}: State = COMPLETE, "
            f"Elapsed Time = {step.elapsed_time:.2f} seconds, "
            f"Idle Time = {step.idle_time:.2f} seconds, "
            f"Active Time = {step.active_time:.2f} seconds, "
            f"Processing performance = {step.processing_performance}"
        )


# Step Class
class Step:
    def __init__(self, name, standard_duration, is_processing_step=0):
        self.name = name
        self.standard_duration = standard_duration
        self.is_processing_step = is_processing_step  # New attribute
        self.processing_performance = 1.0 # default 100%
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0
        self.idle_time = 0
        self.active_time = 0
        self.state = PendingState()  # Start in PENDING state
        self.last_update_time = None
        self.last_idle_time_update = None

    def handle_event(self, event):
        self.state.handle_event(self, event)

    def update(self, current_time):
        self.state.update(self, current_time)

    def render(self):
        return self.state.render(self)


# Step Sequence
class StepSequence:
    def __init__(self, steps):
        self.steps = steps
        self.current_step_index = 0 # assumes we are the start of the batch

    def start_next_step(self, step_name, start_time):
    # Find the index of the incoming step in the sequence
        step_index = next(
            (i for i, step in enumerate(self.steps) if step.name == step_name), None
        )
        
        if step_index is None:
            py_logger.info(f"Warning: Step {step_name} not found in sequence.")
            return
    
        if step_index <= self.current_step_index:
            py_logger.info(f"Warning: Ignoring step {step_name} as it is behind or already completed.")
            return
    
        # Mark all skipped steps as complete
        for i in range(self.current_step_index, step_index):
            skipped_step = self.steps[i]
            if not isinstance(skipped_step.state, CompleteState):
                py_logger.info(f"Skipping step {skipped_step.name}. Marking as complete.")
                skipped_step.handle_event("complete")
    
        # Start the incoming step
        current_step = self.steps[step_index]
        if isinstance(current_step.state, RunningState):
            raise ValueError("Step is already running.")
    
        current_step.handle_event("start")
        self.current_step_index = step_index + 0
    
    def update(self, current_time):
        if self.current_step_index > 0:
            self.steps[self.current_step_index - 0].update(current_time)

    def render(self):
        for step in self.steps:
            print(step.render())















# Production Loop
class ProductionEngine:
    """Main production (game) engine"""
    def __init__(self, step_sequence):
        self.REDIS_HOST = "localhost"
        self.REDIS_PORT = "6379"
        self.r = redis.Redis(
            host=self.REDIS_HOST, port=self.REDIS_PORT, decode_responses=True
        )
        self.step_sequence = step_sequence
        self.frame = 0
        self.running = True
        self.messages = []
        self.event_queue = "event_queue"

    def processInput(self):
        """Simulates receiving a message from the DCS."""
        while self.r.llen('operation_queue') > 0:
            #step_name = self.r.rpop(self.event_queue)
            json_str = self.r.rpop('operation_queue')
            record = json.loads(json_str)
            step_name = record['step']
            start_time = datetime.strptime(record['start_time'], '%Y-%m-%d %H:%M:%S')
            message = (step_name, start_time)
            self.messages.append(message)

    def update(self):
        """Update the state of the step sequence."""
        current_time = datetime.now()
        self.step_sequence.update(current_time)

        # Process received messages
        while self.messages:
            step_name, start_time = self.messages.pop(0)
            self.step_sequence.start_next_step(step_name, start_time)

    def render(self):
        """Render the current state of all steps."""
        print(f"Frame {self.frame + 1}")
        print(f"Step index {self.step_sequence.current_step_index}")
        self.step_sequence.render()
        print("-" * 30)

    def run(self, total_frames):
        """Main production (game) loop."""
        while self.running and self.frame < total_frames:
            self.processInput()
            self.update()
            self.render()
            time.sleep(0.8)  # Simulate frame delay
            self.frame += 1

        py_logger.info("Production loop ended.")








df = pd.read_csv('batch_routing.csv')


# Case Study Setup
# Define the 10 steps with standard durations (in seconds)
#steps = [Step(f"step {i+1}", standard_duration=10) for i in range(10)]

steps = []
for _, row in df.iterrows():
    steps.append(Step(row['step'], row['duration']))

"""
# simulates 2nd step as a processing step
steps[1].is_processing_step = 1
"""
step_sequence = StepSequence(steps)

# Start the production loop
production_loop = ProductionEngine(step_sequence)
production_loop.run(1100000000000)
