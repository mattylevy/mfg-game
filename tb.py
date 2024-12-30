import time

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

    def process_commands(self):
        print("\nAvailable commands:")
        print("1. add_task <task_name> <resource1:amount1,resource2:amount2>")
        print("2. replenish <resource_name> <amount>")
        print("3. show_status")
        print("4. quit")
        print()

        while True:
            command = input("Enter command: ").strip()

            if command.startswith("add_task"):
                parts = command.split()
                if len(parts) >= 3:
                    task_name = parts[1]
                    resource_requirements = {}
                    try:
                        for resource in parts[2].split(","):
                            name, amount = resource.split(":")
                            resource_requirements[name] = int(amount)
                        self.add_task(Task(task_name, resource_requirements))
                    except ValueError:
                        print("Invalid resource format. Use <resource:amount>.")
                else:
                    print("Invalid command. Use: add_task <task_name> <resource:amount,...>")

            elif command.startswith("replenish"):
                parts = command.split()
                if len(parts) == 3:
                    resource_name = parts[1]
                    amount = int(parts[2])
                    if resource_name in self.resources:
                        self.resources[resource_name].replenish(amount)
                    else:
                        print(f"Resource {resource_name} not found!")
                else:
                    print("Invalid command. Use: replenish <resource_name> <amount>")

            elif command == "show_status":
                self.show_status()

            elif command == "quit":
                print("Exiting game...")
                break

            else:
                print("Invalid command.")

    def show_status(self):
        print("\n--- Current Status ---")
        print("Machines:")
        for machine in self.machines:
            status = f"Busy with {machine.current_task}" if machine.current_task else "Idle"
            print(f"  {machine.name}: {status}")

        print("Resources:")
        for resource in self.resources.values():
            print(f"  {resource.name}: {resource.quantity}")

        print("Task Queue:")
        if self.task_queue:
            for task in self.task_queue:
                print(f"  {task.name} - Requires: {task.resource_requirements}")
        else:
            print("  No tasks in queue.")
        print("----------------------")

    def run(self):
        print("Welcome to the Manufacturing Engine!")
        print("Managing your production in real time...\n")
        try:
            while True:
                print("\n--- Engine Loop ---")
                # Check if tasks can be assigned to machines
                for task in self.task_queue:
                    if all(self.resources[res].quantity >= req for res, req in task.resource_requirements.items()):
                        for machine in self.machines:
                            if machine.current_task is None:
                                machine.assign_task(task.name)
                                for res, req in task.resource_requirements.items():
                                    self.resources[res].consume(req)
                                self.task_queue.remove(task)
                                break

                # Update all machines
                for machine in self.machines:
                    machine.update()

                # Simulate time passing
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nGame paused.")
            self.process_commands()

# Example usage
if __name__ == "__main__":
    engine = ManufacturingEngine()

    # Add resources
    engine.add_resource(Resource("Material A", 100))
    engine.add_resource(Resource("Material B", 50))

    # Add machines
    engine.add_machine(Machine("Mixer", task_time=5))
    engine.add_machine(Machine("Packer", task_time=3))

    # Start the engine
    engine.run()