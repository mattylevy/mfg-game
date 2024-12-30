import time
import random
import redis
import json

# Notes #
# Instead of a "game engine" we call this a Business Engine - a business is just an enitity which is a collection of workflows which create value


class BusinessEngine:
    def __init__(self):
        # Initialise the Redis db - this helps drive the "R" in 
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.engine_start_time = time.time()
        self.command_queue = 'command_queue'
        
        
    def workflow_input(self):
        
        # for each new command issued
        while self.r.llen(self.command_queue) > 0:
            command_data = self.r.rpop(self.command_queue)
            #_, command_json = command_data ** Future build - json payload for actions
            #action = json.loads(command_json) ** Future build - json payload for actions
            _, action = command_data
            
            # Take action - need action processing function. What
            # Business logic. What does that action mean? Does it even influence the business state, does it change something. If SO....How does it influence the business state, WHAT IS THE OUTCOME OF THAT ACTION

            
        
    def run(self):
        """ Business(game) loop """
        last_time = time.time()
        target_fps = 0.5  # Slower FPS to make it more readable in this simulation - can we call this clock rate? Or something other to diffrentiate from a game but its the same principle
        frame_duration = 1.0 / target_fps


        while True:
            current_time = time.time()
            delta_time = current_time - last_time

            # Ensure non-negative sleep duration
            sleep_duration = frame_duration - delta_time
            if sleep_duration > 0:
                time.sleep(sleep_duration)

            if delta_time >= frame_duration:

                #self.process_input()  # Process any workflow inputs
                #self.update_business_state(delta_time)  # Update production and resources
                #self.render()  # Display the current state of the factory as just a text output

                last_time = current_time


#engine = BusinessEngine()
#engine.run()