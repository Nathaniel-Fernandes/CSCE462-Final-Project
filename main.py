import os
import time
import json
import binascii
from dotenv import load_dotenv

import FiniteStateMachine as FSM

# import globals as gb

# import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BOARD)
# GPIO.setwarnings(False)

def main():

    # set up RFID reader
    
    # begin Finite State Machine
    try:
        FSM.FSM(FSM.STATES.reset)
        while True:
            response = input("Waiting for input. Please press enter what you want to do: SCAN, DRAWOPEN, DRAWCLOSE, CLOSE:")

            if response == "SCAN":
                # print("result 1: ", reader.SetQ(5))
                # print("result 2: ", reader.SetQ1(5))
                n = FSM.reader.Inventory(False)    # Perform inventory scan

                print("Tags found: ", n)
                tags = list()

                for i in range(n):
                    tag = FSM.reader.GetResult(i)
                    # tag.line()

                    data = {
                        "EPC": binascii.hexlify(tag.EPC).decode('utf-8').upper(),
                        "RSSI": tag.RSSI,
                        "COUNT": tag.Count
                    }

                    tags.append(data)
                # print(tags)

                if len(tags) > 0:
                    res = FSM.db.table('events').insert({
                        "event": "scan_result",
                        "cabinet_id": 1,
                        "scan_result": json.dumps(tags)
                    }).execute()

                    print(res)
                
                else:
                    print("nothing to insert")
            
            elif response == "DRAWOPEN":
                res = FSM.db.table('events').insert({
                    "event": "drawer_open",
                    "cabinet_id": 1
                }).execute()

                print("draw open?", res)

            elif response == "DRAWCLOSE":
                res = FSM.db.table('events').insert({
                    "event": "drawer_close",
                    "cabinet_id": 1
                }).execute()

                print("draw closed?", res)

            elif response == "CLOSE":
                FSM.reader.ClosePort()
                break;

    except BaseException as e:
        FSM.reader.ClosePort()
        print("exception thrown", str(e))

if ( __name__ == "__main__"):
    main()
    # GPIO.cleanup()