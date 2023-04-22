import time
from enum import Enum
import helpers
import globals as gb

#####################################
##########    FSM HELPERS    ########
#####################################

# limit scans to once per door being closed (not continuously scanning)
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
            INSTRUCTIONS.reset_values,
            INSTRUCTIONS.setup_reader
        ],
    },

    # drawer is closed - waiting for open
    STATES.drawer_closed: {
        "instructions": [
            INSTRUCTIONS.check_if_door_is_closed,
            INSTRUCTIONS.send_drawer_closed_status_event,
            INSTRUCTIONS.check_if_scanned,
        ]
    },

    # Cabinet drawer is open
    STATES.drawer_open: {
        "instructions": [
            INSTRUCTIONS.send_drawer_opened_status_event,
        ]
    },

    # UHF Reader is scanning
    STATES.scanning: {
        "instructions": [
            INSTRUCTIONS.run_scan
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
    print("\n[STATE] ", state)

    curr_state = CABINET_STATE[state]
    
    next_state: STATES|None
    condition: CONDITIONS|None
    next_execution_context: EXECUTION_CONTEXT|None

    # A. execute this state's instructions
    for i in curr_state["instructions"]:
        next_state, condition, next_execution_context = execute(i, execution_context)

        if any([next_state, condition, next_execution_context]):
            break

    # B. transition condition
    # TODO: can we implement a FSM interrupt?
    while not isConditionMet(condition):
        time.sleep(3) # so CPU doesn't burn up
    
    # C. Use tail recursion to transition indefinitely
    return FSM(next_state, next_execution_context)

# list: [instruction name, [...parameters]]
def execute(instruction: str, execution_context: str|None):
    ''' Execute the instructions of the FSM'''
    print("[EXEC] ", instruction, execution_context)

    # DONE
    if instruction == INSTRUCTIONS.reset_values:
        try:
            has_scanned = False

            print("Reader: ", gb.reader, id(gb.reader))

            gb.reader.ClosePort()

        except BaseException as e:
            print("Reader already closed", str(e))
        
        return None, None, None

    # DONE: 
    elif instruction == INSTRUCTIONS.setup_reader:
        try:
            gb.reader = helpers.SetupReader()
            print("reader: ", gb.reader, id(gb.reader))
        except BaseException as e:
            print("could not connect to reader", str(e))

        return STATES.drawer_closed, CONDITIONS.immediate, None

    elif instruction == INSTRUCTIONS.check_if_door_is_closed:
        # if true, the door started OPEN not closed
        # if (GPIO.input(setup.BUTTON)): # TODO: fix
        if (bool(input("Enter if door is open: (hit enter for door closed)"))):
            return STATES.drawer_open, CONDITIONS.immediate, EXECUTION_CONTEXT.suppress_sending_event_messages
        
        else:
            global time_of_most_recent_door_close
            time_of_most_recent_door_close = time.time()

            return None, None, None

    elif instruction == INSTRUCTIONS.send_drawer_closed_status_event:
        global time_of_most_recent_door_open
        time_of_most_recent_door_open = time.time()

        try:
            if execution_context != EXECUTION_CONTEXT.suppress_sending_event_messages:
                res = db.table('events').insert({
                    "event": "drawer_close",
                    "cabinet_id": 1,
                    # "user" # TODO: implement authentication - who opened, when, what did they take out?
                }).execute()
                print("drawer close?", res)

        except:
            print("Couldn't send drawer open message")

        finally:
            return None, None, None

    
    elif instruction == INSTRUCTIONS.check_if_scanned:
        if has_scanned:
            return STATES.drawer_open, CONDITIONS.wait_for_door_to_open, None
        
        else:
            return STATES.scanning, CONDITIONS.immediate, None

    elif instruction == INSTRUCTIONS.run_scan:
        if has_scanned:
            return STATES.drawer_closed, CONDITIONS.immediate, EXECUTION_CONTEXT.suppress_sending_event_messages
        
        status_code = helpers.RunScan(0)

        # the reader could not find any tags. restart FSM.
        if status_code == 0:
            return STATES.reset, CONDITIONS.immediate, None
        
        has_scanned=True
        return STATES.drawer_closed, CONDITIONS.immediate, EXECUTION_CONTEXT.suppress_sending_event_messages
    
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
            except BaseException as e:
                print("Couldn't send drawer open status event", str(e))
        
        return STATES.drawer_closed, CONDITIONS.wait_for_door_to_close, None
    
    else:
        print("did not match any instructions!!!: ", instruction, execution_context)
        # TODO: this will throw an error, determine best course of action - maybe go to reset?

def isConditionMet(condition):
    print("[COND] ", condition)

    if condition == CONDITIONS.immediate:
        return True
    
    elif condition == CONDITIONS.wait_for_door_to_open:
        # TODO: modify interrupt code here
        # need 10 door open events to confirm the door has ACTUALLY been open (and not just circuit accidentally jostling around and breaking)

        times_detected_true = 0
        while times_detected_true <= 10:
            if input("is the door open? (type yes)"):
                times_detected_true += 1
                time.sleep(0.2)
            else:
                times_detected_true = 0

        return True

    elif condition == CONDITIONS.wait_for_door_to_close:
        # TODO: modify interrupt code here

        times_detected_true = 0
        while times_detected_true <= 10:
            if input("is the door currently closed? (type yes)"):
                times_detected_true += 1
                time.sleep(0.2)
            else:
                times_detected_true = 0

        return True
    

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
    
# def interrupt():
#     while True:
#         GPIO.wait_for_edge(setup.DRAWER_CLOSE_SWITCH_GPIO, GPIO.rising)

#         # Use to add a cooldown delay
#         if time.time() - setup.COOLDOWN > 20:
#             break
#         else:
#             time.sleep(0.1)

#     return True