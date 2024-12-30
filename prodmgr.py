import time
import random
import os

def clear_console():
    """Clears the console for updated display."""
    os.system('cls' if os.name == 'nt' else 'clear')

class ProductionManager:
    def __init__(self):
        self.resources = 10000  # Initial resources (e.g., raw materials)
        self.finances = 5000    # Initial money available
        self.inventory = 0      # Finished goods inventory
        self.production_rate = 0  # Goods produced per day
        self.machines = []      # List of machines in the factory
        self.workers = []       # List of workers in the factory
        self.time_of_day = 0    # Time progress, e.g., hours in a workday
        self.production_goals = 100  # Example production goal
        self.output = ""        # Output string to store all print statements

    def process_input(self):
        # Simulate random user decisions like adding machines, changing goals, or assigning workers
        events = ["Add machine", "Hire worker", "Increase production goal", "Purchase raw materials"]
        event = random.choice(events)
        
        if event == "Add machine":
            self.machines.append("Machine")
            self.output += f"\nEvent: Added a new machine!"
        elif event == "Hire worker":
            self.workers.append("Worker")
            self.output += f"\nEvent: Hired a new worker!"
        elif event == "Increase production goal":
            self.production_goals += 10
            self.output += f"\nEvent: Increased production goal to {self.production_goals}"
        elif event == "Purchase raw materials":
            self.resources += 500
            self.output += f"\nEvent: Purchased raw materials!"

    def update_game_state(self, delta_time):
        # Update the production process, worker productivity, and machine status
        self.time_of_day += delta_time
        if self.time_of_day >= 24:
            self.time_of_day = 0  # Reset after 24 hours to simulate day/night cycle
            self.finances -= 100  # Example of daily running costs

        # Example of production update
        self.inventory += self.production_rate
        self.resources -= self.production_rate * 2  # Assume each unit of product takes resources

    def handle_ai(self):
        # Handle AI for machines breaking down, workers' productivity, and external factors
        # No output needed for AI handling
        if len(self.machines) > 0 and random.random() < 0.1:  # 10% chance for breakdown
            self.machines = self.machines[:-1]  # Simulate a machine breakdown
        if len(self.workers) > 0 and random.random() < 0.05:  # 5% chance for worker fatigue
            self.workers = self.workers[:-1]  # Simulate a worker leaving temporarily

    def update_world(self):
        # Update world variables like workers' productivity and machine efficiency

        # Simulate worker and machine efficiency
        if self.machines:
            self.production_rate = len(self.machines) * 5  # Each machine produces 5 units per day
        else:
            self.production_rate = 0  # No machines, no production

        if self.resources <= 0:
            self.output += "\nOut of resources! Need to purchase more."
            self.finances -= 200  # Example cost for purchasing more raw materials

    def render(self):
        # Clear the console screen and update the game state
        clear_console()

        # Start with the factory status information
        status_output = f"""
        Factory Status:
        Inventory: {self.inventory} units
        Resources: {self.resources} units
        Finances: ${self.finances}
        Production Rate: {self.production_rate} units/day
        Production Goal: {self.production_goals} units
        Time of Day: {self.time_of_day}/24 hours
        Machines: {len(self.machines)}
        Workers: {len(self.workers)}
        """

        # Append additional outputs such as events, warnings
        self.output = status_output + self.output
        
        # Print the output once all events are processed
        print(self.output)
        
        # Reset the output for the next frame
        self.output = ""

    def run(self):
        last_time = time.time()
        target_fps = 0.5  # Slower FPS to make it more readable in this simulation
        frame_duration = 1.0 / target_fps

        while True:
            current_time = time.time()
            delta_time = current_time - last_time

            # Occasionally skip an action for randomness
            if random.random() < 0.2:  # 20% chance to skip an action
                time.sleep(frame_duration - delta_time)
                continue  # Skip the rest of the loop and wait for the next frame

            if delta_time >= frame_duration:
                self.process_input()  # Simulate random user input
                self.update_game_state(delta_time)  # Update production and resources
                self.handle_ai()  # Simulate machine breakdowns and AI events
                self.update_world()  # Update machine and worker efficiency
                self.render()  # Display the current state of the factory

                last_time = current_time
            else:
                time.sleep(frame_duration - delta_time)

# Run the Production Manager game loop
game = ProductionManager()
game.run()