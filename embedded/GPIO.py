# import RPi.GPIO as GPIO # uncomment 4 pi
import time
import threading
import colors

# setup board
# GPIO.setmode(GPIO.BOARD) # uncomment 4 pi
# GPIO.setwarnings(False) # uncomment 4 pi

who_unlocked_the_door = ''
time_of_last_unlock = time.time() - 60 # starts @ 1 min ago to lock instantly

# define pins
LOCK_OUTPUT = 36
LOCK_INPUT = 16
DOOR_CIRCUIT = 15

# GPIO.setup(LOCK_OUTPUT, GPIO.OUT) # uncomment 4 pi
# GPIO.setup(LOCK_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # uncomment 4 pi
# GPIO.setup(DOOR_CIRCUIT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # uncomment 4 pi

# GETTERS
def IsDoorUnlocked() -> bool:
    '''
        0 -> electromagnet off -> door locked -> false == bool(0)
        1 -> electromagnet on -> door unlocked -> true == bool(1)
    '''
    # val = bool(GPIO.input(LOCK_INPUT)) # uncomment 4 pi
    val = bool(input("Is door locked? <enter> = unlocked, y = locked")) # 4 windows
    colors.print_color("[OUTPUT] Is door locked? %r" % bool(val), "log")
    return val

def IsDoorClosed() -> bool:
    '''
        1 = input high -> circuit unbroken -> door closed
        0 = input low -> circuit broken -> door open
    '''

    # return bool(GPIO.input(DOOR_CIRCUIT)) # 4 pi
    return bool(input("Is door closed? <enter> = open, y = closed")) # 4 windows

def IsDoorOpen():
    return not bool(IsDoorClosed())

# business logic
def ClosePins():
    # GPIO.cleanup() # 4 pi
    pass # 4 windows
    
def LockDoor():
    # GPIO.output(LOCK_OUTPUT, GPIO.LOW) # 4 pi
    colors.print_color("[LOCKED] Drawer locked successfully.", "success")

def UnlockDoor():
    global time_of_last_unlock
    time_of_last_unlock = time.time()
    # GPIO.output(LOCK_OUTPUT, GPIO.HIGH) # 4 pi
    colors.print_color("[UNLOCK] Drawer unlocked successfully at %.2f" % time_of_last_unlock, "success")

def WaitForDoorToOpen():
    if IsDoorOpen():
        return True
    
    while True:
        # use polling to check if door is open 10x to ensure falling edge was not an accident
        times_detected_true = 0
        while times_detected_true < 10:
            time.sleep(0.3)
            if IsDoorOpen():
                times_detected_true += 1
            else:
                times_detected_true = 0 
    
        return True
    
def WaitForDoorToClose():
    if IsDoorClosed():
        return True
    
    while True:
        # use polling to check if door is open 10x to ensure falling edge was not an accident
        times_detected_true = 0
        while times_detected_true < 10:
            time.sleep(0.3)
            if IsDoorClosed():
                times_detected_true += 1
            else:
                times_detected_true = 0 
    
        return True

thread = None
def LockDoorEvery60Sec():
    global thread

    colors.print_color("[LOCKED] Security Measure - Attempting to lock drawer every 60 seconds.", "warning")
    if IsDoorClosed() and time.time() > 60 + time_of_last_unlock:
        LockDoor()

    if thread != None:
        thread.cancel()

    thread = threading.Timer(60.0, LockDoorEvery60Sec).start()
    

LockDoorEvery60Sec()
