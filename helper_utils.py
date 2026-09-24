import time
import random

def random_wait():
    """Pauses the script for a random duration between 5 and 10 seconds."""
    # random.uniform generates a random decimal (e.g., 7.42), which makes it look more human
    wait_time = random.uniform(5, 10) 
    print(f"Waiting for {wait_time:.2f} seconds...")
    time.sleep(wait_time)