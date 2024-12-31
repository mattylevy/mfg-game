import time


class GameObject:
    def __init__(self, name, build_time):
        self.name = name
        self.build_time = build_time
        self.remaining_build_time = build_time
        self.status = "Not Started"

    def update(self, delta_time):
        if self.status == "Building":
            self.remaining_build_time -= delta_time
            if self.remaining_build_time <= 0:
                self.remaining_build_time = 0
                self.status = "Constructed"

    def start_construction(self):
        if self.status == "Not Started":
            self.status = "Building"

    def pause_construction(self):
        if self.status == "Building":
            self.status = "Paused"

    def resume_construction(self):
        if self.status == "Paused":
            self.status = "Building"

    def render(self):
        return f"{self.name}: Status = {self.status}, Remaining Build Time = {self.remaining_build_time:.2f}"


class ObjectManager:
    def __init__(self):
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def get_object(self, name):
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None

    def update_objects(self, delta_time):
        for obj in self.objects:
            obj.update(delta_time)

    def render_objects(self):
        for obj in self.objects:
            print(obj.render())


class GameLoop:
    def __init__(self, object_manager):
        self.object_manager = object_manager
        self.frame = 0
        self.delta_time = 1  # Simulating 1-second intervals per frame.
        self.running = True

    def handle_events(self):
        """Simulate commands at specific frames."""
        if self.frame == 5:
            print("\n--- Command: Start Refinery Construction ---")
            refinery = self.object_manager.get_object("Refinery")
            if refinery:
                refinery.start_construction()
        elif self.frame == 15:
            print("\n--- Command: Pause Refinery Construction ---")
            refinery = self.object_manager.get_object("Refinery")
            if refinery:
                refinery.pause_construction()
        elif self.frame == 20:
            print("\n--- Command: Resume Refinery Construction ---")
            refinery = self.object_manager.get_object("Refinery")
            if refinery:
                refinery.resume_construction()

    def update(self):
        """Update the state of all game objects."""
        self.object_manager.update_objects(self.delta_time)

    def render(self):
        """Render the state of the game."""
        print(f"Frame {self.frame + 1}")
        self.object_manager.render_objects()
        print("-" * 30)

    def run(self, total_frames):
        """Main game loop."""
        while self.running and self.frame < total_frames:
            self.handle_events()
            self.update()
            self.render()
            time.sleep(0.1)  # Simulate frame delay
            self.frame += 1

        print("Game loop ended.")


# Set up the game world.
object_manager = ObjectManager()

# Add a building to the object manager.
refinery = GameObject("Refinery", build_time=10)
object_manager.add_object(refinery)

# Start the game loop.
game_loop = GameLoop(object_manager)
game_loop.run(300)