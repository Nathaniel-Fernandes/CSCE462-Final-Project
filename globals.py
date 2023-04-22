import os
from dotenv import load_dotenv
from supabase import create_client, Client 

# one instance, used everywhere
# TODO: do I even need the keyword global?
# global reader
# global db

reader = None
print("id of reader: ", id(reader))
db = None

# open connection to database
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
db: Client = create_client(url, key)