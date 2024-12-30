import os

def interactive_water_glass(max_height=5):
    # Initial water level
    water_level = 0

    while True:
        # Calculate the water level percentage
        water_percentage = int((water_level / max_height) * 100)

        # Start creating the glass
        glass = " -----\n"
        for i in range(max_height):
            if i < max_height - water_level:
                glass += "|     |\n"  # Empty space in the glass
            else:
                glass += "|#####|\n"  # Water fills the bottom rows
        glass += " -----"
        
        # Clear the previous output
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print the glass and water level
        print(glass)
        print(f"Water level: {water_percentage}%")
        print("\nCommands: [fill] Add water, [drain] Remove water, [exit] Quit")

        # Get user input
        command = input("Enter a command: ").strip().lower()

        # Process commands
        if command == "fill":
            if water_level < max_height:
                water_level += 1
            else:
                print("The glass is already full!")
        elif command == "drain":
            if water_level > 0:
                water_level -= 1
            else:
                print("The glass is already empty!")
        elif command == "exit":
            print("Goodbye!")
            break
        else:
            print("Invalid command! Please use [fill], [drain], or [exit].")

# Start the interactive game
interactive_water_glass()