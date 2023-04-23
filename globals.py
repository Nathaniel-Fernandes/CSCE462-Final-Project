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
    fetched_authorized_personnel = list(map(lambda d: d['authorized_personnel'], res.data))
    
    if set(authorized_personnel) != set(fetched_authorized_personnel):
        authorized_personnel = fetched_authorized_personnel
        print("[AUSER] Personnel authorized to open this cabinet have IDs: ", authorized_personnel)    
 
    if thread1 != None:
        thread1.cancel()
        
    thread1 = threading.Timer(10.0, get_authorized_personnel).start()
    
get_authorized_personnel() 

# C2 Listen for remote unlock events
thread2 = None
num_of_remote_unlock_events = None
def get_remote_unlock_events():
    global thread2
    global num_of_remote_unlock_events
    
    res = db.table("events").select("*").eq("event", "remote_unlock").execute()
       
    new_num_found = len(res.data)
    
    if new_num_found > num_found:
        num_found = new_num_found
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