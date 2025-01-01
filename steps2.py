import time
from datetime import datetime, timedelta
import redis

import os



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
        self.elapsed_time = 0
        self.idle_time = 0  # New attribute to accumulate idle time
        self.state = StepState.PENDING
        self.last_idle_time_update = None  # To track when the step entered IDLE state

    def start(self, start_time):
        self.start_time = start_time
        self.state = StepState.RUNNING
        self.last_idle_time_update = None  # Reset idle time tracking when step starts

    def complete(self, end_time):
        self.end_time = end_time
        self.elapsed_time = (self.end_time - self.start_time).total_seconds()
        self.state = StepState.COMPLETE
        self.last_idle_time_update = None  # Reset idle time tracking when step completes

    def update(self, current_time):
        # Update elapsed_time when running or idle
        if self.state == StepState.RUNNING or self.state == StepState.IDLE:
            self.elapsed_time = (current_time - self.start_time).total_seconds()

        if self.state == StepState.RUNNING and self.elapsed_time > self.standard_duration:
            self.state = StepState.IDLE
            self.last_idle_time_update = current_time  # Track the time when the step enters IDLE

        if self.state == StepState.IDLE:
            # Accumulate idle time only when the step is in IDLE state
            self.idle_time += (current_time - self.last_idle_time_update).total_seconds()
            self.last_idle_time_update = current_time  # Update the last idle time

    def render(self):
        """ Render output method """
        
        return (
            f"Step {self.name}: State = {self.state}, "
            f"Start = {self.start_time}, End = {self.end_time}, "
            f"Elapsed Time = {self.elapsed_time:.2f} seconds, "
            f"Idle Time = {self.idle_time:.2f} seconds"
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
        def clear_console():
            """Clears the console for updated display."""
            os.system('cls' if os.name == 'nt' else 'clear')
            
        clear_console()
        for step in self.steps:
            print(step.render())


# Production Loop
class ProductionEngine:
    """ Main production (game) engine """
    def __init__(self, step_sequence):
        # config vars
        self.REDIS_HOST = 'localhost'
        self.REDIS_PORT = '6379'
        # Initialise the Redis db - this helps drive the "R" in "RTS"
        self.r = redis.Redis(host=self.REDIS_HOST, port=self.REDIS_PORT, decode_responses=True)
        self.step_sequence = step_sequence
        self.frame = 0
        self.running = True
        self.messages = []
        self.event_queue = 'event_queue'

    def processInput(self):
        """
        Simulates receiving a message from the DCS.
        Returns a tuple: (step_name, datetime).
        """
        print(self.r.llen(self.event_queue))
        # for each new event
        while self.r.llen(self.event_queue) > 0:
 
            step_name = self.r.rpop(self.event_queue)
            message = (step_name, datetime.now())
            self.messages.append(message) # appends message to list of recieved messages in the ProudctionEngine object
            print(message)
            
    def update(self):
        """Update the state of the step sequence."""
        current_time = datetime.now()
        self.step_sequence.update(current_time)
        
        # Process the recieved messages
        while len(self.messages) > 0:
            step_name, start_time = self.messages.pop(0)
            self.step_sequence.start_next_step(step_name, start_time)
            

    def render(self):
        """Render the current state of all steps."""
        print(f"Frame {self.frame + 1}")
        self.step_sequence.render()
        print("-" * 30)

    def run(self, total_frames):
        """Main production(game) loop."""
        while self.running and self.frame < total_frames:
            
            
            # Core production loop functions --- following game loop framework 
            self.processInput()
            self.update()
            self.render()
            
            # Timing control
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