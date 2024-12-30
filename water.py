import os
import time

def clear_console():
    """Clears the console for updated display."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_glass(water_level, max_height):
    """Displays the glass with the current water level and percentage."""
    water_percentage = int((water_level / max_height) * 100)
    glass = " -----\n"
    for i in range(max_height):
        if i < max_height - water_level:
            glass += "|     |\n"  # Empty space in the glass
        else:
            glass += "|#####|\n"  # Water-filled rows
    glass += " -----"
    glass += " \n "
    print(glass)
    print(f"Water level: {water_percentage}%")

def interactive_water_glass(max_height=5):
    """Interactive water glass game with filling and draining animations."""
    water_level = 0

    while True:
        # Display the glass and available commands
        clear_console()
        display_glass(water_level, max_height)
        print("\nCommands: [fill] Add water, [drain] Remove water, [exit] Quit")
        
        # Get user input
        command = input("Enter a command: ").strip().lower()

        if command == "fill":
            # Incrementally fill the glass
            while water_level < max_height:
                water_level += 1
                clear_console()
                display_glass(water_level, max_height)
                time.sleep(0.3)  # Simulate filling animation
            print("The glass is now full!")
        elif command == "drain":
            # Incrementally drain the glass
            while water_level > 0:
                water_level -= 1
                clear_console()
                display_glass(water_level, max_height)
                time.sleep(0.3)  # Simulate draining animation
            print("The glass is now empty!")
        elif command == "exit":
            print("Goodbye!")
            break
        else:
            print("Invalid command! Please use [fill], [drain], or [exit].")
            time.sleep(1)

# Start the interactive game
interactive_water_glass()