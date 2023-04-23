import time
from enum import Enum
import helpers
import globals as gb
import GPIO as gpio
import colors

#####################################
##########    FSM HELPERS    ########
#####################################

# limit scans to once per door being closed (not continuously scanning)
has_scanned = False

CONDITIONS = Enum("CONDITIONS", ["immediate", "wait_for_door_to_open", "wait_for_door_to_close"])
STATES = Enum("STATES", ["reset", "drawer_closed", "drawer_open", "drawer_unlocked", "scanning"])
EXECUTION_CONTEXT = Enum("EXECUTION_CONTEXT", ["suppress_sending_event_messages", "sleep_10_sec"])
INSTRUCTIONS = Enum("INSTRUCTIONS", [
    "reset_values", "setup_reader", 
    "check_if_door_is_closed", 
    "send_drawer_closed_status_event", "send_drawer_opened_status_event",
    "check_if_scanned", "run_scan",
    "check_for_authorized_access_card", "unlock_door", "send_drawer_unlocked_status_event", "lock_door",  # new
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
            INSTRUCTIONS.lock_door,
            INSTRUCTIONS.send_drawer_closed_status_event,
            INSTRUCTIONS.check_if_scanned,
            INSTRUCTIONS.check_for_authorized_access_card
        ]
    },

    STATES.drawer_unlocked: {
        "instructions": [
            INSTRUCTIONS.unlock_door,
            INSTRUCTIONS.send_drawer_unlocked_status_event
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

def FSM(state: str, execution_context=None, instruction_start_idx=0):
    ''' 
        This function implements a finite state machine (FSM).
        As with any FSM, there are two parts: the current state and the transition condition.

        param execution_context contains information from the previous state that impacts the execution of this 
        current state's instructions 
    '''
    colors.print_color("\n\n[STATE] %s" % state, "log")

    curr_state = CABINET_STATE[state]
    
    next_state: STATES
    condition: CONDITIONS
    next_execution_context: EXECUTION_CONTEXT

    # A. execute this state's instructions, optionally skipping some instructions
    for i in range(instruction_start_idx, len(curr_state["instructions"])):
        instruction = curr_state["instructions"][i]

        next_state, condition, next_execution_context, next_instruction_start_index = execute(instruction, execution_context)
        
        time.sleep(1) # delay next instruction so output is more human readable
        
        # go to another state before finishing this one's instructions?
        if any([next_state, condition, next_execution_context]):
            break

    # B. transition condition
    # TODO: can we implement a FSM interrupt?
    while not isConditionMet(condition):
        time.sleep(3) # so CPU doesn't burn up
    
    # C. Use tail recursion to transition indefinitely
    return FSM(next_state, next_execution_context, next_instruction_start_index)

# list: [instruction name, [...parameters]]
def execute(instruction: str, execution_context: str):
    ''' Execute the instructions of the FSM
        Note: returning 'None None None' proceeds to next instruction.
        Returning anything else jumps to the specified state.
    '''
    colors.print_color("[XCUTE] %s %s" % (instruction, execution_context), "log")

    global has_scanned

    if instruction == INSTRUCTIONS.reset_values:
        try:
            has_scanned = False
            gb.reader.ClosePort()
            time.sleep(3) # give 3 seconds to allow reader to reboot

            if execution_context == EXECUTION_CONTEXT.sleep_10_sec:
                time.sleep(10)
                
        except BaseException as e:
            colors.print_color("[ERROR] reader already closed: %s" % str(e), "error")
        
        return None, None, None, 0

    elif instruction == INSTRUCTIONS.setup_reader:
        try:
            gb.reader = helpers.SetupReader()

        except BaseException as e:
            colors.print_color("[ERROR] could not connect to reader: %s" % str(e), "error")
            return STATES.reset, CONDITIONS.immediate, EXECUTION_CONTEXT.sleep_10_sec, 0

        return STATES.drawer_closed, CONDITIONS.immediate, EXECUTION_CONTEXT.suppress_sending_event_messages, 0

    elif instruction == INSTRUCTIONS.check_if_door_is_closed:
        # if true, the door started OPEN not closed
        # if (bool(input("Enter if door is open: (hit enter for door closed)"))):
        if gpio.IsDoorOpen():
            return STATES.drawer_open, CONDITIONS.immediate, EXECUTION_CONTEXT.suppress_sending_event_messages, 0
        
        return None, None, None, 0
    
    elif instruction == INSTRUCTIONS.lock_door:
        gpio.LockDoor()
        return None, None, None, 0
    
    elif instruction == INSTRUCTIONS.send_drawer_opened_status_event:
        if execution_context != EXECUTION_CONTEXT.suppress_sending_event_messages:
            try:
                # reset scan value once the door has been opened
                has_scanned = False

                # TODO: could extract this if wanted
                res = gb.db.table('events').insert({
                    "event": "drawer_open",
                    "cabinet_id": 1,
                }).execute()

                colors.print_color("[RESPO] Inserted drawer open event successfully.", "success")

            except BaseException as e:
                colors.print_color("[ERROR] Failed to send drawer open event: %s" % str(e), "error")
        
        return STATES.drawer_closed, CONDITIONS.wait_for_door_to_close, None, 0

    elif instruction == INSTRUCTIONS.send_drawer_closed_status_event:
        try:
            if execution_context != EXECUTION_CONTEXT.suppress_sending_event_messages:
                # TODO: might be extracted to helper function
                res = gb.db.table('events').insert({
                    "event": "drawer_close",
                    "cabinet_id": 1,
                }).execute()
                
                colors.print_color("[RESPO] Inserted drawer closed status event successfully.", "success")
        except BaseException as e:
            colors.print_color("[ERROR] Failed to send drawer closed status event: %s" % str(e), "error")

        finally:
            return None, None, None, 0

    elif instruction == INSTRUCTIONS.check_if_scanned:
        if has_scanned:
            return None, None, None, 0
        
        else:
            return STATES.scanning, CONDITIONS.immediate, None, 0

    elif instruction == INSTRUCTIONS.run_scan:
        if not has_scanned:
            status_code, _ = helpers.RunScan(0, True)

            # the reader could not find any tags. restart FSM.
            if status_code == 0:
                return STATES.reset, CONDITIONS.immediate, EXECUTION_CONTEXT.sleep_10_sec, 0
        
            has_scanned=True

        return STATES.drawer_closed, CONDITIONS.immediate, EXECUTION_CONTEXT.suppress_sending_event_messages, 3
    
    elif instruction == INSTRUCTIONS.check_for_authorized_access_card:
        while True and gpio.IsDoorLocked():
            colors.print_colors("[AWAIT] Waiting for authorized personnel to badge in.", "log")

            # checks every 2 sec to prevent burning up CPU
            time.sleep(2)

            status_code, tags = helpers.RunScan(0, False)

            # the reader could not find any tags. restart FSM.
            if status_code == 0:
                return STATES.reset, CONDITIONS.immediate, None, 0
        
            else:
                detected_epcs = list(map(lambda x: x["EPC"], tags))
                matches = set(gb.authorized_personnel).intersection(set(detected_epcs))
            
                if (len(matches) > 0):
                    gpio.who_unlocked_the_door = list(matches)[0]
                    colors.print_color("[AUSER] Authorized user who opened door: %s" % gpio.who_unlocked_the_door, "blue")
                    break

        return STATES.drawer_unlocked, CONDITIONS.immediate, None, 0

    elif instruction == INSTRUCTIONS.unlock_door:
        gpio.UnlockDoor()

        return None, None, None, 0

    elif instruction == INSTRUCTIONS.send_drawer_unlocked_status_event:
        try:
            if execution_context != EXECUTION_CONTEXT.suppress_sending_event_messages:
                # TODO: might be extracted to helper function
                res = gb.db.table('events').insert({
                    "event": "drawer_unlocked",
                    "cabinet_id": 1,
                    "user": gpio.who_unlocked_the_door
                }).execute()
                
                colors.print_color("[RESPO] Sent drawer unlocked status event successfully.", "success")

        except BaseException as e:
            colors.print_color("[ERROR] Failed to send drawer open message: %s" % str(e), "error")

        finally:
            return STATES.drawer_open, CONDITIONS.wait_for_door_to_open, None, 0
        
    else:
        print("[DANGER] Instruction did not match any instructions: ", instruction, execution_context)

def isConditionMet(condition):
    colors.print_color("[CHECK] Running the following condition: %s" % condition, "log")

    if condition == CONDITIONS.immediate:
        return True
    
    elif condition == CONDITIONS.wait_for_door_to_open:
        return gpio.WaitForDoorToOpen()

    elif condition == CONDITIONS.wait_for_door_to_close:
        return gpio.WaitForDoorToClose()