import time
import random

# Define the entities in the manufacturing process
class Machine:
    def __init__(self, name, task_time):
        self.name = name
        self.task_time = task_time  # Time it takes to complete a task
        self.current_task = None
        self.time_remaining = 0

    def assign_task(self, task):
        if self.current_task is None:
            self.current_task = task
            self.time_remaining = self.task_time
            print(f"{self.name} started task: {task}")
        else:
            print(f"{self.name} is busy!")

    def update(self):
        if self.current_task:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                print(f"{self.name} finished task: {self.current_task}")
                self.current_task = None

class Resource:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

    def consume(self, amount):
        if self.quantity >= amount:
            self.quantity -= amount
            print(f"Consumed {amount} of {self.name}. Remaining: {self.quantity}")
        else:
            print(f"Not enough {self.name} available!")

    def replenish(self, amount):
        self.quantity += amount
        print(f"Replenished {amount} of {self.name}. Total: {self.quantity}")

class Task:
    def __init__(self, name, resource_requirements):
        self.name = name
        self.resource_requirements = resource_requirements  # Dict of required resources

# Game loop equivalent
class ManufacturingEngine:
    def __init__(self):
        self.machines = []
        self.resources = {}
        self.task_queue = []

    def add_machine(self, machine):
        self.machines.append(machine)

    def add_resource(self, resource):
        self.resources[resource.name] = resource

    def add_task(self, task):
        self.task_queue.append(task)
        print(f"Task added: {task.name}")

    def run(self):
        while True:
            print("\n--- Engine Loop ---")
            # Check if tasks can be assigned to machines
            for task in self.task_queue:
                # Check if resources are available
                if all(self.resources[res].quantity >= req for res, req in task.resource_requirements.items()):
                    # Assign the task to an idle machine
                    for machine in self.machines:
                        if machine.current_task is None:
                            machine.assign_task(task.name)
                            # Consume resources
                            for res, req in task.resource_requirements.items():
                                self.resources[res].consume(req)
                            self.task_queue.remove(task)
                            break

            # Update all machines
            for machine in self.machines:
                machine.update()

            # Simulate time passing
            time.sleep(1)

# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = ManufacturingEngine()

    # Add resources
    engine.add_resource(Resource("Material A", 100))
    engine.add_resource(Resource("Material B", 50))

    # Add machines
    engine.add_machine(Machine("Mixer", task_time=5))
    engine.add_machine(Machine("Packer", task_time=3))

    # Add tasks
    engine.add_task(Task("Mix Batch 1", {"Material A": 10}))
    engine.add_task(Task("Pack Batch 1", {"Material B": 5}))
    engine.add_task(Task("Mix Batch 2", {"Material A": 15}))

    # Run the engine
    engine.run()