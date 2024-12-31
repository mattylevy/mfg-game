import time
from datetime import datetime, timedelta
import redis

# Step FSM States
class StepState:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    IDLE = "IDLE"

# Step Class
class Step:
    def __init__(self, name, standard_duration, is_timer=False):
        self.name = name
        self.standard_duration = standard_duration  # Expected duration for the step
        self.is_timer = is_timer  # Determines if this is a timer-based step
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0  # Total time since the step started
        self.active_time = 0  # Time spent in the RUNNING state
        self.idle_time = 0  # Cumulative idle time
        self.idle_events = []  # List of idle events as (start_time, end_time, duration, description)
        self.state = StepState.PENDING
        self.performance = None  # Performance percentage, calculated at the end
        self.performance_calculated = False

    def start(self, start_time):
        self.start_time = start_time
        self.state = StepState.RUNNING

    def complete(self, end_time):
        self.end_time = end_time
        self.elapsed_time = (self.end_time - self.start_time).total_seconds()
        if not self.performance_calculated:
            self.calculate_performance()
            self.performance_calculated = True
        self.state = StepState.COMPLETE

    def update(self, current_time):
        if self.state in {StepState.RUNNING, StepState.IDLE}:
            self.elapsed_time = (current_time - self.start_time).total_seconds()

        if self.state == StepState.RUNNING:
            self.active_time = self.elapsed_time - self.idle_time
            if self.is_timer and self.active_time >= self.standard_duration:
                self.generate_idle_event(current_time)

        if self.state == StepState.IDLE:
            self.update_idle_event(current_time)

    def generate_idle_event(self, current_time):
        self.state = StepState.IDLE
        idle_start = current_time
        self.idle_events.append((idle_start, None, 0, ""))  # Start a new idle event

    def update_idle_event(self, current_time):
        if self.idle_events:
            idle_event = self.idle_events[-1]
            idle_start, _, _, _ = idle_event
            idle_duration = (current_time - idle_start).total_seconds()
            self.idle_events[-1] = (idle_start, current_time, idle_duration, "")
            self.idle_time = sum(event[2] for event in self.idle_events)

    def calculate_performance(self):
        if self.elapsed_time > 0:
            self.performance = (self.active_time / self.elapsed_time) * 100
        else:
            self.performance = 100  # Default to 100% if no time has elapsed

    def render(self):
        result = (
            f"Step {self.name}: State = {self.state}, "
            f"Start = {self.start_time}, End = {self.end_time}, "
            f"Elapsed Time = {self.elapsed_time:.2f} seconds, "
            f"Active Time = {self.active_time:.2f} seconds, "
            f"Idle Time = {self.idle_time:.2f} seconds, "
            f"Performance = {self.performance:.2f}%" if self.performance is not None else ""
        )
        result += f", Idle Events = {len(self.idle_events)}"
        for idx, event in enumerate(self.idle_events, 1):
            result += (
                f"\n    Idle Event {idx}: Start = {event[0]}, End = {event[1]}, "
                f"Duration = {event[2]:.2f}s"
            )
        return result

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

# Case Study Setup
steps = [
    Step(f"Step {i + 1}", standard_duration=10, is_timer=(i % 2 == 0))
    for i in range(10)
]
step_sequence = StepSequence(steps)

# Redis setup
REDIS_HOST = "localhost"
REDIS_PORT = 6379
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Run production loop
class ProductionEngine:
    def __init__(self, step_sequence):
        self.step_sequence = step_sequence
        self.frame = 0
        self.running = True
        self.messages = []
        self.event_queue = "event_queue"

    def process_input(self):
        while r.llen(self.event_queue) > 0:
            step_name = r.rpop(self.event_queue)
            message = (step_name, datetime.now())
            self.messages.append(message)

    def update(self):
        current_time = datetime.now()
        self.step_sequence.update(current_time)

        # Process the received messages
        while len(self.messages) > 0:
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

# Start production loop
production_loop = ProductionEngine(step_sequence)
production_loop.run(110)