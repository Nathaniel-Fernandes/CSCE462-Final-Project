import time
from enum import Enum
import helpers

# TODO: Extract to a setup file
reader = helpers.SetupReader()

# load env file
import os
from dotenv import load_dotenv
from supabase import create_client, Client
load_dotenv()

# open connection to database
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
db: Client = create_client(url, key)

#####################################
##########    FSM HELPERS    ########
#####################################
has_scanned = False

CONDITIONS = Enum("CONDITIONS", ["immediate", "wait_for_door_to_open", "wait_for_door_to_close"])
STATES = Enum("STATES", ["reset", "drawer_closed", "drawer_open", "scanning"])
EXECUTION_CONTEXT = Enum("EXECUTION_CONTEXT", ["suppress_sending_event_messages"])
INSTRUCTIONS = Enum("INSTRUCTIONS", [
    "reset_values", "setup_reader", "check_if_door_is_closed", "send_drawer_closed_status_event", "check_if_scanned",
    "send_drawer_opened_status_event", "run_scan"
])

CABINET_STATE = {
    # reset to initial
    STATES.reset: {
        "instructions": [
            [INSTRUCTIONS.reset_values],
            [INSTRUCTIONS.setup_reader]
        ],
    },

    # drawer is closed - waiting for open
    STATES.drawer_closed: {
        "instructions": [
            [INSTRUCTIONS.check_if_door_is_closed],
            [INSTRUCTIONS.send_drawer_closed_status_event],
            [INSTRUCTIONS.check_if_scanned],
        ]
    },

    # Cabinet drawer is open
    STATES.drawer_open: {
        "instructions": [
            [INSTRUCTIONS.send_drawer_opened_status_event],
        ]
    },

    # UHF Reader is scanning
    STATES.scanning: {
        "instructions": [
            [INSTRUCTIONS.run_scan]
        ]
    }
}

#####################################
##########    FUNCTIONS    ##########
#####################################

def FSM(state: str, execution_context=None):
    ''' 
        This function implements a finite state machine (FSM).
        As with any FSM, there are two parts: the current state and the transition condition.

        param execution_context contains information from the previous state that impacts the execution of this 
        current state's instructions 
    '''
    curr_state = CABINET_STATE[state]
    
    next_state: STATES|None
    condition: CONDITIONS|None
    params: EXECUTION_CONTEXT|None

    # A. execute this state's instructions
    for i in curr_state["instructions"]:
        next_state, condition, params = execute(i, execution_context)

        if any([next_state, condition, params]):
            break

    # B. transition condition
    # TODO: can we implement a FSM interrupt?
    while not isConditionMet(condition, params):
        time.sleep(1) # so CPU doesn't burn up
    
    # C. Use tail recursion to transition indefinitely
    return FSM(next_state)

# list: [instruction name, [...parameters]]
def execute(instruction: str, execution_context: str|None):
    ''' Execute the instructions of the FSM'''
    if instruction == INSTRUCTIONS.reset_values:
        try:
            has_scanned = False
            reader.ClosePort()
        except:
            print("Reader already closed")

    elif instruction == INSTRUCTIONS.setup_reader:
        try:
            reader = helpers.SetupReader()
        except:
            print("could not connect to reader")

        return STATES.drawer_closed, CONDITIONS.immediate, None

    elif instruction == INSTRUCTIONS.check_if_door_is_closed:
        # if true, the door started open not closed
        if (GPIO.input(setup.BUTTON)):
            return STATES.drawer_open, CONDITIONS.immediate, EXECUTION_CONTEXT.suppress_sending_event_messages

    elif instruction == INSTRUCTIONS.send_drawer_closed_status_event:
        if execution_context == EXECUTION_CONTEXT.suppress_sending_event_messages:
            return
        
        else:
            try:
                res = db.table('events').insert({
                    "event": "drawer_close",
                    "cabinet_id": 1,
                    # "user" # TODO: implement authentication - who opened, when, what did they take out?
                }).execute()
                print("drawer close?", res)
            except:
                print("Couldn't send drawer open message")
    
    elif instruction == INSTRUCTIONS.check_if_scanned:
        if has_scanned:
            return STATES.drawer_open, CONDITIONS.wait_for_door_to_open, None
        
        else:
            return STATES.scanning, CONDITIONS.immediate, None

    elif instruction == INSTRUCTIONS.run_scan:
        if has_scanned:
            return STATES.drawer_closed, CONDITIONS.immediate, EXECUTION_CONTEXT.suppress_sending_event_messages
        
        status_code = helpers.RunScan(reader, db, 0)

        # the reader could not find any tags. restart FSM.
        if status_code == 0:
            return STATES.reset, CONDITIONS.immediate, None
        
        has_scanned=True
    
    elif instruction == INSTRUCTIONS.send_drawer_opened_status_event:
        if execution_context != EXECUTION_CONTEXT.suppress_sending_event_messages:
            try:
                # reset scan value once the door has been opened
                has_scanned = False

                res = db.table('events').insert({
                    "event": "drawer_open",
                    "cabinet_id": 1
                }).execute()

                print("draw open?", res)
            except:
                print("Couldn't send drawer open status event")
        
        return STATES.drawer_closed, CONDITIONS.wait_for_door_to_close, None
    
    else:
        print("did not match any instructions!!!: ", instruction, execution_context)
        # TODO: this will throw an error, determine best course of action

def isConditionMet(condition, conditionParams):
    if condition == CONDITIONS.immediate:
        return True
    
    elif condition == CONDITIONS.wait_for_door_to_open:
        # TODO: modify interrupt code here
        input("hit enter when door has opened: ")

    elif condition == CONDITIONS.wait_for_door_to_close:
        # TODO: modify interrupt code here
        input("hit enter when door has closed: ")
    

    # if condition == "countdown":
    #     while updateCounter() > conditionParams:
    #         if conditionParams == 0: # hard coded, checks if we're doing state4
    #             blink(setup.PED_BLUE, 1, 0.4, 0.4)
    #         time.sleep(0.2)
    #     return True
    
    # if condition == "button_press":
    #     interrupt()
        
    #     setup.COOLDOWN = time.time()
    #     setup.COUNTDOWN_START_TIME = time.time()

    #     return True
    
def interrupt():
    while True:
        GPIO.wait_for_edge(setup.DRAWER_CLOSE_SWITCH_GPIO, GPIO.rising)

        # Use to add a cooldown delay
        if time.time() - setup.COOLDOWN > 20:
            break
        else:
            time.sleep(0.1)

    return True