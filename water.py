import os
import time
import threading

# Shared variables to manage the state
water_level = 0
max_height = 5
is_running = False
current_action = None  # Tracks the current action ("fill", "drain")

def clear_console():
    """Clears the console for updated display."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_glass():
    """Displays the glass with the current water level and percentage."""
    global water_level, max_height
    water_percentage = int((water_level / max_height) * 100)
    glass = " -----\n"
    for i in range(max_height):
        if i < max_height - water_level:
            glass += "|     |\n"  # Empty space in the glass
        else:
            glass += "|#####|\n"  # Water-filled rows
    glass += " -----"
    clear_console()
    print(glass)
    print(f"Water level: {water_percentage}%")

def animate(action):
    """Handles the animation for filling or draining."""
    global water_level, max_height, is_running, current_action
    while is_running:
        if action == "fill" and water_level < max_height:
            water_level += 1
        elif action == "drain" and water_level > 0:
            water_level -= 1
        else:
            # Stop if we reach the boundary
            is_running = False
            current_action = None
            break
        display_glass()
        time.sleep(0.3)  # Animation delay

def interactive_water_glass():
    """Interactive game engine with multithreaded commands."""
    global is_running, current_action

    while True:
        display_glass()
        print("\nCommands: [fill] Add water, [drain] Remove water, [stop] Stop current action, [exit] Quit")
        
        # Listen for user input
        command = input("Enter a command: ").strip().lower()

        if command == "fill" or command == "drain":
            if is_running:
                print("An action is already running! Use 'stop' to interrupt.")
                time.sleep(1)
                continue
            
            # Start the action in a new thread
            is_running = True
            current_action = command
            threading.Thread(target=animate, args=(command,), daemon=True).start()
        
        elif command == "stop":
            if is_running:
                print("Stopping the current action...")
                is_running = False
                current_action = None
            else:
                print("No action is currently running!")
            time.sleep(1)

        elif command == "exit":
            if is_running:
                print("Stopping the current action before exiting...")
                is_running = False
            print("Goodbye!")
            break

        else:
            print("Invalid command! Please use [fill], [drain], [stop], or [exit].")
            time.sleep(1)

# Start the interactive game
interactive_water_glass()