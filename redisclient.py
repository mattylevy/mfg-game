import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("\nCommands: [add_asset] Add a new asset, [remove_asset] Removes an asset, [exit] Quit")

while True:
     # Get user input
    command = input("Enter a command: ").strip()
    
    r.lpush('event_queue',command)