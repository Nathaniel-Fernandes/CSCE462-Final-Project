import os
from dotenv import load_dotenv
from supabase import create_client, Client 
# from realtime.connection import Socket
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

# C2. Create socket connection for real-time listening
# TODO: too complicated, couldn't figure out

# async def updateAP(payload):
#     global authorized_personnel

#     res = db.table('cabinet').select('authorized_personnel').execute()
#     authorized_personnel = list(map(lambda d: d['authorized_personnel'], res.data))
#     print("ap: ", authorized_personnel)

# realtime = db.realtime.from('cabinet').on("*", updateAP).subscribe()

# async def listen():
#     URL = f"wss://zpwpgqucpronyregatse.supabase.co/realtime/v1/websocket?apikey={key}&vsn=1.0.0"
#     socket = Socket(URL)
#     socket.connect()
#     channel1 = socket.set_channel("realtime:*")
#     channel1.join().on("*", updateAP)
#     await socket.listen()
# socket.listen()s
# async def listen_for_AP_changes():
    # return socket.listen()    
