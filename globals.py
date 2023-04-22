import os
from dotenv import load_dotenv
from supabase import create_client, Client 

# one instance, used everywhere
reader = None
db = None

# open connection to database
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
db: Client = create_client(url, key)

print("gb db original: ", id(db))
