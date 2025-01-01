import time
from datetime import datetime
import redis
from abc import ABC, abstractmethod


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
            print(f"Step {step.name} started.")

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
            print(f"Step {step.name} completed.")

    def update(self, step, current_time):
        step.active_time += (current_time - step.last_update_time).total_seconds()
        step.last_update_time = current_time

        # Transition to IDLE if active_time exceeds standard_duration
        if step.active_time > step.standard_duration:
            step.state = IdleState()
            step.last_idle_time_update = current_time
            print(f"Step {step.name} is now IDLE.")

    def render(self, step):
        return (
            f"Step {step.name}: State = RUNNING, "
            f"Active Time = {step.active_time:.2f} seconds"
        )


class IdleState(StepState):
    def handle_event(self, step, event):
        if event == "resume":
            step.state = RunningState()
            step.last_update_time = datetime.now()
            print(f"Step {step.name} resumed.")

    def update(self, step, current_time):
        step.idle_time += (current_time - step.last_idle_time_update).total_seconds()
        step.last_idle_time_update = current_time

    def render(self, step):
        return (
            f"Step {step.name}: State = IDLE, "
            f"Idle Time = {step.idle_time:.2f} seconds"
        )


class CompleteState(StepState):
    def handle_event(self, step, event):
        pass  # No events are processed in COMPLETE state

    def update(self, step, current_time):
        pass  # No updates in COMPLETE state

    def render(self, step):
        return (
            f"Step {step.name}: State = COMPLETE, "
            f"Elapsed Time = {step.elapsed_time:.2f} seconds"
        )


# Step Class
class Step:
    def __init__(self, name, standard_duration):
        self.name = name
        self.standard_duration = standard_duration
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
        self.current_step_index = 0

    def start_next_step(self, step_name, start_time):
        if self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]

            # Ensure the correct step is starting
            if current_step.name == step_name:
                if isinstance(current_step.state, RunningState):
                    raise ValueError("Step is already running.")

                # Mark previous step as complete
                if self.current_step_index > 0:
                    self.steps[self.current_step_index - 1].handle_event("complete")

                # Start the current step
                current_step.handle_event("start")
                self.current_step_index += 1

    def update(self, current_time):
        if self.current_step_index > 0:
            self.steps[self.current_step_index - 1].update(current_time)

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
        while self.r.llen(self.event_queue) > 0:
            step_name = self.r.rpop(self.event_queue)
            message = (step_name, datetime.now())
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

        print("Production loop ended.")


# Case Study Setup
# Define the 10 steps with standard durations (in seconds)
steps = [Step(f"step {i+1}", standard_duration=10) for i in range(10)]
step_sequence = StepSequence(steps)

# Start the production loop
production_loop = ProductionEngine(step_sequence)
production_loop.run(110)