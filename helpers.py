import lib.j421xlib as j421xlib
import binascii
import json
import time
import signal
from typing import Tuple
import globals as gb
import colors

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

signal.signal(signal.SIGALRM, timeout_handler)

def SetupReader():
    # load the library
    f = j421xlib.J4210()
    ver = f.LibVersion()

    # if it takes longer than 10 sec, something is wrong.
    signal.alarm(10)

    # Get & Connect to a port
    ports = f.AvailablePorts()
    # f.OpenPort(ports[1], 57600) # 4 windows
    f.OpenPort(ports[0], 57600) # 4 pi
    
    # Log data about reader for debugging purposes
    colors.print_color("[READER] Lib Version: %s" % ver, "log")
    colors.print_color('[READER] Last Error: %s' % f.LastError(), "log")
    colors.print_color("[READER] Available Serial Ports: %s" % str(ports), "log")
    reader_info = f.LoadSettings()
    reader_info.echo()
    
    signal.alarm(0)

    return f

# Runs a scan, updates the DB, and returns # of tags found
def RunScan(runtimes=0, updateDB=False) -> Tuple[int, list]:
    if runtimes > 3:
        return 0
    
    n = gb.reader.Inventory(False)    # Perform inventory scan

    colors.print_color("[SCANNED] Tags found: %d" % n, "log")
    tags = list()

    for i in range(n):
        tag = gb.reader.GetResult(i)

        data = {
            "EPC": binascii.hexlify(tag.EPC).decode('utf-8').upper(),
            "RSSI": tag.RSSI,
            "COUNT": tag.Count
        }

        tags.append(data)

    if len(tags) <= 0:
        colors.print_color("[WARNING] Found no tags. Running again in 2 seconds.", "warning")
        time.sleep(1)
        RunScan(runtimes+1)

    elif updateDB:
        try:
            res = gb.db.table('events').insert({
                "event": "scan_result",
                "cabinet_id": 1,
                "scan_result": json.dumps(tags),
                "cabinet_id": gb.cabinet_id
            }).execute()
            
            colors.print_color("[RESPONSE] Successfully inserted tags into database", "success")
            
        except BaseException as e:
            colors.print_color("[ERROR] Failed to update table with tags: %s" % str(e), "error")
        
    return n, tags

def SendWarningMessage(id="UNKNOWN"):

    if gb.manager_number != None:
        message = gb.client.messages \
                .create(
                     body="Unauthorized access attempt to Cabinet %s. Likely suspect: %s. Please check immediately." % (gb.cabinet_id, id),
                     from_='+18883035570',
                     to=gb.manager_number
                 )
        
        colors.print_color("[SUCCESS] Message sent successfully.", "success")

    else:
        colors.print_color("[ERROR] Could not load manager's number.", "error")