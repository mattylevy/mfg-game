import psycopg2
import pandas as pd
import time
import json
import redis
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
TABLE_NAME = os.getenv("TABLE_NAME")
PLANT_FILTER = os.getenv("PLANT_FILTER")  # Filter for plant (e.g., "PlantA")
UNIT_FILTER = os.getenv("UNIT_FILTER")    # Filter for unit (e.g., "Unit1")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))  # Default to 10 seconds if not set

# Redis Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DECODE_RESPONSES = True
REDIS_LIST_NAME = "operation_queue"

# Initialize Redis client
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=REDIS_DECODE_RESPONSES)

# Function to fetch the current batch records for the filtered plant and unit
def get_current_batch_records():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        
        # Query to get the latest record for the filtered plant and unit
        latest_batch_query = f"""
        SELECT batch_id
        FROM {TABLE_NAME}
        WHERE site = %s AND unit = %s
        ORDER BY id DESC
        LIMIT 1;
        """
        cursor.execute(latest_batch_query, (PLANT_FILTER, UNIT_FILTER))
        latest_batch_id = cursor.fetchone()
        
        if not latest_batch_id or latest_batch_id[0] is None:
            print(f"No records found for site '{PLANT_FILTER}' and unit '{UNIT_FILTER}'.")
            return None, pd.DataFrame()

        batch_id = latest_batch_id[0]
        
        # Query to get all records associated with the latest batch ID for the filtered plant and unit
        batch_records_query = f"""
        SELECT id, step, start_time
        FROM {TABLE_NAME}
        WHERE batch_id = %s AND site = %s AND unit = %s
        ORDER BY id ASC;
        """
        cursor.execute(batch_records_query, (batch_id, PLANT_FILTER, UNIT_FILTER))
        records = cursor.fetchall()
        
        df = pd.DataFrame(records, columns=["id", "step", "start_time"])
        return batch_id, df

    except Exception as e:
        print(f"Error fetching current batch records: {e}")
        return None, pd.DataFrame()

    finally:
        if connection:
            cursor.close()
            connection.close()

# Function to fetch new records for the filtered plant and unit since the last ID
def get_new_records(last_id):
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        
        new_records_query = f"""
        SELECT id, step, start_time
        FROM {TABLE_NAME}
        WHERE id > %s AND site = %s AND unit = %s
        ORDER BY id ASC;
        """
        cursor.execute(new_records_query, (last_id, PLANT_FILTER, UNIT_FILTER))
        records = cursor.fetchall()
        
        df = pd.DataFrame(records, columns=["id", "step", "start_time"])
        return df

    except Exception as e:
        print(f"Error fetching new records: {e}")
        return pd.DataFrame()

    finally:
        if connection:
            cursor.close()
            connection.close()

# Function to push record to Redis
def push_to_redis(step, start_time):
    try:
        # Create JSON message to be pushed to Redis
        record = {
            "step": step,
            "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime object
        }
        # Convert the dictionary to a JSON string
        json_record = json.dumps(record)
        
        # Push to Redis list
        r.lpush(REDIS_LIST_NAME, json_record)
        print(f"Pushed to Redis: {json_record}")

    except Exception as e:
        print(f"Error pushing record to Redis: {e}")

# Main loop
def poll_new_steps():
    current_batch_id, batch_df = get_current_batch_records()
    if current_batch_id is None:
        print("Exiting: No records found for the specified plant and unit.")
        return

    print(f"Current batch ID: {current_batch_id}")
    print(f"Initial records:\n{batch_df[['step', 'start_time']]}")

    last_id = batch_df["id"].max() if not batch_df.empty else 0

    # Push initial records to Redis
    for _, row in batch_df.iterrows():
        push_to_redis(row['step'], row['start_time'])

    while True:
        print(f"Polling for new records since ID {last_id} for site '{PLANT_FILTER}' and unit '{UNIT_FILTER}'...")
        new_records_df = get_new_records(last_id)
        
        if not new_records_df.empty:
            last_id = new_records_df["id"].max()
            new_records_df = new_records_df[["step", "start_time"]]
            for _, row in new_records_df.iterrows():
                push_to_redis(row['step'], row['start_time'])
            print(f"New records found and pushed to Redis.")
        else:
            print("No new records found.")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    poll_new_steps()