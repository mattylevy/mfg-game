import time
from datetime import datetime, timedelta


# Step FSM States
class StepState:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    IDLE = "IDLE"


# Step Object
class Step:
    def __init__(self, name, standard_duration):
        self.name = name
        self.standard_duration = standard_duration  # Expected duration for the step
        self.start_time = None
        self.end_time = None
        self.current_duration = 0
        self.state = StepState.PENDING

    def start(self, start_time):
        self.start_time = start_time
        self.state = StepState.RUNNING

    def complete(self, end_time):
        self.end_time = end_time
        self.current_duration = (self.end_time - self.start_time).total_seconds()
        self.state = StepState.COMPLETE

    def update(self, current_time):
        if self.state == StepState.RUNNING:
            self.current_duration = (current_time - self.start_time).total_seconds()
            if self.current_duration > self.standard_duration:
                self.state = StepState.IDLE

    def render(self):
        return (
            f"Step {self.name}: State = {self.state}, "
            f"Start = {self.start_time}, End = {self.end_time}, "
            f"Current Duration = {self.current_duration:.2f} seconds"
        )


# StepSequence Manager
class StepSequence:
    def __init__(self, steps):
        self.steps = steps  # Ordered list of Step objects
        self.current_step_index = 0

    def start_next_step(self, step_name, start_time):
        if self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]

            # Ensure the correct step is starting
            if current_step.name == step_name:
                if current_step.state == StepState.RUNNING:
                    raise ValueError("Step is already running.")

                # Mark previous step as complete
                if self.current_step_index > 0:
                    self.steps[self.current_step_index - 1].complete(start_time)

                # Start the current step
                current_step.start(start_time)
                self.current_step_index += 1

    def update(self, current_time):
        if self.current_step_index < len(self.steps):
            self.steps[self.current_step_index - 1].update(current_time)

    def render(self):
        for step in self.steps:
            print(step.render())


# Production Loop
class ProductionLoop:
    def __init__(self, step_sequence):
        self.step_sequence = step_sequence
        self.frame = 0
        self.running = True

    def receive_dcs_message(self):
        """
        Simulates receiving a message from the DCS.
        Returns a tuple: (step_name, datetime).
        """
        messages = {
            5: ("Step 1", datetime.now()),
            10: ("Step 2", datetime.now() + timedelta(seconds=5)),
            15: ("Step 3", datetime.now() + timedelta(seconds=10)),
        }
        return messages.get(self.frame)

    def update(self):
        """Update the state of the step sequence."""
        current_time = datetime.now()
        self.step_sequence.update(current_time)

        # Simulate DCS message
        message = self.receive_dcs_message()
        if message:
            step_name, start_time = message
            self.step_sequence.start_next_step(step_name, start_time)

    def render(self):
        """Render the current state of all steps."""
        print(f"Frame {self.frame + 1}")
        self.step_sequence.render()
        print("-" * 30)

    def run(self, total_frames):
        """Main production loop."""
        while self.running and self.frame < total_frames:
            self.update()
            self.render()
            time.sleep(0.1)  # Simulate frame delay
            self.frame += 1

        print("Production loop ended.")


# Case Study Setup
# Define the 10 steps with standard durations (in seconds)
steps = [Step(f"Step {i+1}", standard_duration=10) for i in range(10)]
step_sequence = StepSequence(steps)

# Start the production loop
production_loop = ProductionLoop(step_sequence)
production_loop.run(20)