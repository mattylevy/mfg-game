import time
import sys

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

        glass += " -----\n"

        # Print the glass with the updated water level
        sys.stdout.write(f'\r{glass}')
        sys.stdout.flush()
        
        # Simulate a delay to show the filling effect
        time.sleep(0.2)
    
    print()  # Move to the next line after the filling is complete

# Example usage: Fill the glass in 20 steps
water_glass_fill(20)