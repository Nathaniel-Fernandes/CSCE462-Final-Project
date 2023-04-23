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
    f.OpenPort(ports[1], 57600)

    # Log data about reader for debugging purposes
    print("Lib Version: ", ver)
    print('Last Error: ', f.LastError())
    print("Available Serial Ports:", ports)
    reader_info = f.LoadSettings()
    reader_info.echo()

    return f

# Runs a scan, updates the DB, and returns # of tags found
def RunScan(runtimes=0, updateDB=False) -> Tuple[int, list]:
    if runtimes > 3:
        return 0
    
    n = gb.reader.Inventory(False)    # Perform inventory scan

    print("Tags found: ", n)
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
        print("Found no tags. Running again in 2 seconds.")
        time.sleep(1)
        RunScan(runtimes+1)

    elif updateDB:
        try:
            res = gb.db.table('events').insert({
                "event": "scan_result",
                "cabinet_id": 1,
                "scan_result": json.dumps(tags)
            }).execute()
            print(res)
        except BaseException as e:
            print("Could not update table w/ tags", str(e))
        
    return n, tags


# def interrupt():
#     while True:
#         GPIO.wait_for_edge(setup.DRAWER_CLOSE_SWITCH_GPIO, GPIO.rising)

#         # Use to add a cooldown delay
#         if time.time() - setup.COOLDOWN > 20:
#             break
#         else:
#             time.sleep(0.1)

#     return True