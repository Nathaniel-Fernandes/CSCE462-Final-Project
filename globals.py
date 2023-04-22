import os
from dotenv import load_dotenv
from supabase import create_client, Client 
from realtime.connection import Socket

# one instance, used everywhere
reader = None
db = None
authorized_personnel = []

# open connection to database
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
db: Client = create_client(url, key)

# Create socket connection for real-time listening
def updateAP(payload):
    global authorized_personnel

    res = db.table('cabinet').select('authorized_personnel').execute()
    authorized_personnel = list(map(lambda d: d['authorized_personnel'], res.data))

URL = f"wss://zpwpgqucpronyregatse.supabase.co/realtime/v1/websocket?apikey={key}&vsn=1.0.0"
s = Socket(URL)
s.connect()

channel_1 = s.set_channel("realtime:*")
channel_1.join().on("*", updateAP)
s.listen()
