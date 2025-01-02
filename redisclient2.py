import redis
import json
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


test = r.rpop('operation_queue')

if test:
    record = json.loads(test)

datetime_str = record['start_time']

start_time = datetime.strptime(record['start_time'], '%Y-%m-%d %H:%M:%S')