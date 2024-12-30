import time
import os

def water_glass_fill(total_steps, max_height=5):
    for step in range(total_steps + 1):
        # Calculate the water level, the number of rows of water in the glass
        water_level = int((step / total_steps) * max_height)
        
        # Start creating the glass
        glass = " -----\n"
        for i in range(max_height):
            if i < max_height - water_level:
                glass += "|     |\n"  # Empty space in the glass
            else:
                glass += "|#####|\n"  # Water fills the bottom rows
        glass += " -----"
        
        # Add a line below the glass to display the current level
        text = f"Water level: {water_level}/{max_height}"

        # Clear the previous output
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print the updated glass and the current water level
        print(glass)
        print(text)

        # Simulate a delay to show the filling effect
        time.sleep(0.2)

# Example usage: Fill the glass in 20 steps
water_glass_fill(20)