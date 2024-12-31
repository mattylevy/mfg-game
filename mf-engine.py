import time
import redis
import os

# Notes #
# Instead of a "game engine" we call this a Business Engine - a business is just an enitity which is a collection of workflows which create value


class BusinessEngine:
    def __init__(self):
        # Initialise the Redis db - this helps drive the "R" in 
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.engine_start_time = time.time()
        self.command_queue = 'command_queue'
        self.frame = 0
        
        # game world
        self.assets = 0
    
        
        
    def process_input(self):
        """ Method to process the command queue """
        # for each new command issued
        while self.r.llen(self.command_queue) > 0:
            command_data = self.r.rpop(self.command_queue)
            #print(command_data)
            #_, command_json = command_data ** Future build - json payload for actions
            #action = json.loads(command_json) ** Future build - json payload for actions
            action = command_data
            
            # execute process action logic
            self.process_action(action)
            
    def process_action(self, action):
        """ 
        Method to define how actions are processed. 
        Tells us what each command does and allows us to simulate business logic.
        """
        # Take action - need action processing function. What
        # Business logic. What does that action mean? Does it even influence the business state, 
        # does it change something. If SO....How does it influence the business state, WHAT IS THE OUTCOME OF THAT ACTION
        
        if action =='add_asset':
            self.assets += 1
        elif action == 'remove_asset':
            self.assets -= 1


    def update_state(self):
        """ Method to update business state """
        self.water_level = 0
        self.max_height = 5
        



    def render(self):
        """ Render output method """
        
        def clear_console():
            """Clears the console for updated display."""
            os.system('cls' if os.name == 'nt' else 'clear')
            
        clear_console()
        print('Engine running...')
        print(f'Frame... {self.frame}')
        print(f'Assets = {self.assets}')
       

        
    def run(self):
        """ Business(game) loop """
        last_time = time.time()
        target_fps = 5  # Slower FPS to make it more readable in this simulation - can we call this clock rate? Or something other to diffrentiate from a game but its the same principle
        frame_duration = 1.0 / target_fps

        while True:
            current_time = time.time()
            delta_time = current_time - last_time
            

            # Ensure non-negative sleep duration
            sleep_duration = frame_duration - delta_time
            if sleep_duration > 0:
                time.sleep(sleep_duration)

            if delta_time >= frame_duration:

                self.frame += 1
                self.process_input()  # Process any  inputs
                self.update_state()  # Update production and resources
                self.render()  # Display the current state of the factory as just a text output

                last_time = current_time


engine = BusinessEngine()
engine.run()