import time
import threading

# Game state variables
running = True
tasks = []
resources = 100

def display_status():
    """Displays the current status of the game."""
    print(f"Resources: {resources}")
    print(f"Tasks in queue: {len(tasks)}")
    print("Tasks:", tasks)

def add_task():
    """Adds a task to the queue."""
    global tasks
    if resources >= 10:
        tasks.append({"name": f"Task {len(tasks)+1}", "remaining_time": 5})
        print(f"Added Task {len(tasks)} (5 seconds to complete).")
    else:
        print("Not enough resources to add a task!")

def process_tasks():
    """Processes tasks in the queue."""
    global tasks, resources
    completed_tasks = []
    for task in tasks:
        task["remaining_time"] -= 1
        if task["remaining_time"] <= 0:
            completed_tasks.append(task)

    for task in completed_tasks:
        tasks.remove(task)
        resources += 5  # Reward for task completion
        print(f"{task['name']} completed! Resources +5.")

def game_loop():
    """Simulates the game engine loop."""
    global running
    while running:
        print("Engine loop running...")
        process_tasks()
        display_status()
        time.sleep(1)

def user_input():
    """Handles user input in a separate thread."""
    global running, resources
    while running:
        command = input("Enter command (add/quit): ").strip().lower()
        if command == "add":
            add_task()
        elif command == "quit":
            print("Exiting game...")
            running = False
        else:
            print("Unknown command. Try 'add' or 'quit'.")

# Start the game loop in a separate thread
game_thread = threading.Thread(target=game_loop, daemon=True)
game_thread.start()

# Start handling user input in the main thread
user_input()

# Wait for the game thread to finish
game_thread.join()