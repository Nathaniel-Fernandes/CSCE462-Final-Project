import os
from dotenv import load_dotenv
from supabase import create_client, Client 
import twilio
import threading
import GPIO as gpio
import colors

# A. one instance, used everywhere
cabinet_id = -1
reader = None
db = None
authorized_personnel = []
all_personnel = []

# B. open connection to database
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
db: Client = create_client(url, key)

# C. Set up phone number
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = twilio.rest.Client(account_sid, auth_token)

manager_number = None
try:
    res = db.table('Users').select('phone_number').eq('role', 'admin').execute()
    manager_number = res.data[0]["phone_number"]
    colors.print_color("Manager's number on file is %s" % manager_number, "warning")

except BaseException as e:
    colors.print_color("[ERROR] Could not retrieve managers' number: %s." % str(e), "error")

# C1. Get authorized personnel
res = db.table('Users').select('uuid').neq('uuid', None).execute()
all_personnel = list(map(lambda d: d['uuid'], res.data))

thread1 = None
def get_authorized_personnel():
    global authorized_personnel
    global thread1    

    # res = db.table('cabinets').select('authorized_personnel').eq('cabinet_id', cabinet_id).neq('authorized_personnel', None).execute()
    res = db.table('Permissions').select('personnel_uuid').eq('cabinet_id', cabinet_id).neq('personnel_uuid', None).execute()
    fetched_authorized_personnel = list(map(lambda d: d['personnel_uuid'], res.data))
    
    if set(authorized_personnel) != set(fetched_authorized_personnel):
        authorized_personnel = fetched_authorized_personnel
        print("[AUSER] Personnel authorized to open Cabinet %u have IDs: " % cabinet_id, authorized_personnel)    
 
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
    
    res = db.table("Events").select("*").eq('cabinet_id', cabinet_id).eq("event", "remote_unlock").execute()
       
    num_found = len(res.data)
    
    if num_of_remote_unlock_events == None:
        num_of_remote_unlock_events = num_found 
        
    else:
        if num_found > num_of_remote_unlock_events:
            # A remote unlock signal has been sent. Unlock the door.
            colors.print_color("[REMOTE] Door remotely unlocked.", "warning")
            gpio.UnlockDoor()
            num_of_remote_unlock_events = num_found
            
    if thread2 != None:
        thread2.cancel()
        
    thread2 = threading.Timer(10.0, get_remote_unlock_events).start()

get_remote_unlock_events()