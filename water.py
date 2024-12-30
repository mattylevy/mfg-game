from consoledraw import Console
import time
import threading

class WaterGame:
    def __init__(self):
        self.console = Console()
        self.running = True
        self.command = None
        self.water_level = 0
        self.max_level = 10
        self.action = None  # Current action (fill or drain)

    def render_glass(self):
        """Render the water glass with the current water level."""
        self.console.clear()
        self.console.print("Water Glass Game", align="center", bold=True)
        self.console.print("+" + "-" * 7 + "+")
        for i in range(self.max_level, 0, -1):
            if self.water_level >= i:
                self.console.print("|███████|")
            else:
                self.console.print("|       |")
        self.console.print("+" + "-" * 7 + "+")
        self.console.print(f"Water Level: {self.water_level * 10}%", align="center")
        self.console.print("Commands: fill, drain, stop, exit", align="center")

    def handle_input(self):
        """Continuously handle user input."""
        while self.running:
            self.command = input("Command (fill, drain, stop, exit): ").strip().lower()

    def fill(self):
        """Fill the water glass."""
        self.action = "fill"
        while self.water_level < self.max_level and self.action == "fill":
            self.water_level += 1
            self.render_glass()
            time.sleep(0.5)

    def drain(self):
        """Drain the water glass."""
        self.action = "drain"
        while self.water_level > 0 and self.action == "drain":
            self.water_level -= 1
            self.render_glass()
            time.sleep(0.5)

    def run(self):
        """Run the game."""
        input_thread = threading.Thread(target=self.handle_input, daemon=True)
        input_thread.start()

        while self.running:
            if self.command == "fill" and self.action != "fill":
                self.fill()
                self.command = None
            elif self.command == "drain" and self.action != "drain":
                self.drain()
                self.command = None
            elif self.command == "stop":
                self.action = None
                self.command = None
            elif self.command == "exit":
                self.running = False
            self.render_glass()
            time.sleep(0.1)

# Run the game
if __name__ == "__main__":
    game = WaterGame()
    game.run()