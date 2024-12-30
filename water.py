import asyncio

class GameEngine:
    def __init__(self):
        self.running = True
        self.command = None
        self.water_level = 0
        self.max_level = 100

    async def get_command(self):
        """Continuously fetch user input asynchronously."""
        while self.running:
            self.command = await asyncio.to_thread(input, "Command (fill, drain, stop, exit): ").strip()

    async def fill(self):
        """Incrementally fill the water tank."""
        while self.water_level < self.max_level:
            if self.command == "stop":
                print("Stopped filling!")
                break
            self.water_level += 10
            await asyncio.sleep(0.5)

    async def drain(self):
        """Incrementally drain the water tank."""
        while self.water_level > 0:
            if self.command == "stop":
                print("Stopped draining!")
                break
            self.water_level -= 10
            await asyncio.sleep(0.5)

    async def render(self):
        """Continuously render the water level."""
        while self.running:
            # Clear the screen and redraw the water glass
            print("\033c", end="")  # ANSI escape sequence to clear the terminal
            print("Water Glass")
            for i in range(self.max_level, -1, -10):
                if self.water_level >= i:
                    print("|███████|")  # Filled line
                else:
                    print("|       |")  # Empty line
            print("Water Level:", self.water_level, "%")
            await asyncio.sleep(0.1)

    async def game_loop(self):
        """Handle game commands and logic."""
        while self.running:
            if self.command == "fill":
                await self.fill()
                self.command = None
            elif self.command == "drain":
                await self.drain()
                self.command = None
            elif self.command == "exit":
                self.running = False
                print("Exiting game...")
            else:
                await asyncio.sleep(0.1)

    async def run(self):
        """Run the game engine."""
        await asyncio.gather(
            self.get_command(),  # Handle user input
            self.render(),       # Continuously render the game state
            self.game_loop()     # Update game logic based on commands
        )

# Start the game engine
if __name__ == "__main__":
    engine = GameEngine()
    asyncio.run(engine.run())