import lib.j421xlib as j421xlib
import binascii
import json
import time
import globals as gb
from typing import Tuple

def SetupReader():
    # load the library
    f = j421xlib.J4210()
    ver = f.LibVersion()

    # Get & Connect to a port
    ports = f.AvailablePorts()
    f.OpenPort(ports[0], 57600)

    # Log data about reader for debugging purposes
    print("[READER] Lib Version: ", ver)
    print('[READER] Last Error: ', f.LastError())
    print("[READER] Available Serial Ports: ", ports)
    reader_info = f.LoadSettings()
    reader_info.echo()

    return f

# Runs a scan, updates the DB, and returns # of tags found
def RunScan(runtimes=0, updateDB=False) -> Tuple[int, list]:
    if runtimes > 3:
        return 0
    
    n = gb.reader.Inventory(False)    # Perform inventory scan

    print("[SCANNED] Tags found: ", n)
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
        print("[WARNING] Found no tags. Running again in 2 seconds.")
        time.sleep(1)
        RunScan(runtimes+1)

    elif updateDB:
        try:
            res = gb.db.table('events').insert({
                "event": "scan_result",
                "cabinet_id": 1,
                "scan_result": json.dumps(tags)
            }).execute()
            
            print("[RESPONSE] Successfully inserted tags into database")
            
        except BaseException as e:
            print("[ERROR] Failed to update table with tags: ", str(e))
        
    return n, tags