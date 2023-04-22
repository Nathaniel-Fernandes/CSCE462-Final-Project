import os
from dotenv import load_dotenv
from supabase import create_client, Client 
import threading

# A. one instance, used everywhere
reader = None
db = None
authorized_personnel = []

# B. open connection to database
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
db: Client = create_client(url, key)

# C1. Get authorized personel initially
def get_authorized_personnel():
    global authorized_personnel
    res = db.table('cabinet').select('authorized_personnel').neq('authorized_personnel', None).execute()
    authorized_personnel = list(map(lambda d: d['authorized_personnel'], res.data))
    print("authorized personnel: ", authorized_personnel)
    threading.Timer(10.0, get_authorized_personnel).start()

get_authorized_personnel() 
