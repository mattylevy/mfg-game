import time
from datetime import datetime
import redis
from abc import ABC, abstractmethod
import json
import logging
import pandas as pd

# Configure Logging
def setup_logger():
    logger = logging.getLogger("ProductionLogger")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler("logfile.log", mode="w")
    formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


logger = setup_logger()


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
            logger.info(f"Step {step.name} started.")

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
            logger.info(f"Step {step.name} completed. Finalized attributes: {step.render()}")

    def update(self, step, current_time):
        step.active_time += (current_time - step.last_update_time).total_seconds()
        step.elapsed_time += (current_time - step.last_update_time).total_seconds()
        step.last_update_time = current_time

        if step.is_processing_step:
            step.processing_performance = min(1.0, step.standard_duration / step.active_time)
        elif step.active_time > step.standard_duration:
            step.state = IdleState()
            step.last_idle_time_update = current_time
            logger.info(f"Step {step.name} transitioned to IDLE.")

    def render(self, step):
        return (
            f"Step {step.name}: State = RUNNING, "
            f"Elapsed Time = {step.elapsed_time:.2f} seconds, "
            f"Active Time = {step.active_time:.2f} seconds, "
            f"Processing Performance = {step.processing_performance:.2f}"
        )


class IdleState(StepState):
    def handle_event(self, step, event):
        if event == "resume":
            step.state = RunningState()
            step.last_update_time = datetime.now()
            logger.info(f"Step {step.name} resumed.")
        elif event == "complete":
            step.end_time = datetime.now()
            step.elapsed_time = (step.end_time - step.start_time).total_seconds()
            step.state = CompleteState()
            logger.info(f"Step {step.name} completed from IDLE state.")

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
            f"Processing Performance = {step.processing_performance:.2f}"
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
            f"Processing Performance = {step.processing_performance:.2f}"
        )


# Step Class
class Step:
    def __init__(self, name, standard_duration, is_processing_step=0):
        self.name = name
        self.standard_duration = standard_duration
        self.is_processing_step = is_processing_step
        self.processing_performance = 1.0
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0
        self.idle_time = 0
        self.active_time = 0
        self.state = PendingState()
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
        self.current_step_index = 0

    def start_next_step(self, step_name, start_time):
        step_index = next(
            (i for i, step in enumerate(self.steps) if step.name == step_name), None
        )
        if step_index is None or step_index <= self.current_step_index:
            logger.info(f"Invalid step transition to {step_name}.")
            return

        for i in range(self.current_step_index, step_index):
            if not isinstance(self.steps[i].state, CompleteState):
                logger.info(f"Skipping step {self.steps[i].name}. Marking as complete.")
                self.steps[i].handle_event("complete")

        self.steps[step_index].handle_event("start")
        self.current_step_index = step_index

    def update(self, current_time):
        if self.current_step_index > 0:
            self.steps[self.current_step_index].update(current_time)

    def render(self):
        for step in self.steps:
            print(step.render())


# Production Engine
class ProductionEngine:
    def __init__(self, step_sequence):
        self.redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.step_sequence = step_sequence
        self.frame = 0
        self.running = True
        self.messages = []

    def process_input(self):
        while self.redis_client.llen("operation_queue") > 0:
            json_str = self.redis_client.rpop("operation_queue")
            record = json.loads(json_str)
            step_name = record["step"]
            start_time = datetime.strptime(record["start_time"], "%Y-%m-%d %H:%M:%S")
            self.messages.append((step_name, start_time))

    def update(self):
        current_time = datetime.now()
        self.step_sequence.update(current_time)

        while self.messages:
            step_name, start_time = self.messages.pop(0)
            self.step_sequence.start_next_step(step_name, start_time)

    def render(self):
        print(f"Frame {self.frame + 1}")
        self.step_sequence.render()
        print("-" * 30)

    def run(self, total_frames):
        while self.running and self.frame < total_frames:
            self.process_input()
            self.update()
            self.render()
            time.sleep(0.8)
            self.frame += 1

        logger.info("Production loop ended.")


# Case Study Setup
df = pd.read_csv("batch_routing.csv")
steps = [Step(row["step"], row["duration"]) for _, row in df.iterrows()]
step_sequence = StepSequence(steps)

# Start the production loop
production_engine = ProductionEngine(step_sequence)
production_engine.run(100)