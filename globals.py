import os
from dotenv import load_dotenv
from supabase import create_client, Client 
import threading
import GPIO as gpio

# A. one instance, used everywhere
reader = None
db = None
authorized_personnel = []

# B. open connection to database
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
db: Client = create_client(url, key)

# C1. Get authorized personnel
thread1 = None
def get_authorized_personnel():
    global authorized_personnel
    global thread1
    
    res = db.table('cabinet').select('authorized_personnel').neq('authorized_personnel', None).execute()
    authorized_personnel = list(map(lambda d: d['authorized_personnel'], res.data))
    
    if thread1 != None:
        thread1.cancel()
        
    thread1 = threading.Timer(10.0, get_authorized_personnel).start()
    print("[AUSER] The personnel authorized to open this cabinet have IDs: ", authorized_personnel)

get_authorized_personnel() 

# C2 Listen for remote unlock events
thread2 = None
num_of_remote_unlock_events = None
def get_remote_unlock_events():
    global thread2
    global num_of_remote_unlock_events
    
    # query = "SELECT COUNT(event) FROM events WHERE event = 'remote_unlock'"
    # res = db.from_params(query)
    res = db.table("events").select("*").eq("event", "remote_unlock").execute()
       
    num_found = len(res.data)
    print("[REMOTE] Number of remote unlock events: ", num_found)
    
    if num_of_remote_unlock_events == None:
        num_of_remote_unlock_events = num_found
        
    else:
        if num_found > num_of_remote_unlock_events:
            # A remote unlock signal has been sent. Unlock the door.
            gpio.UnlockDoor()
            num_of_remote_unlock_events = num_found
    
    if thread2 != None:
        thread2.cancel()
    thread2 = threading.Timer(10.0, get_remote_unlock_events).start()

get_remote_unlock_events()