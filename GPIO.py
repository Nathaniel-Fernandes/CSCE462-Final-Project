import RPi.GPIO as GPIO
import time
import threading
import colors

# setup board
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

who_unlocked_the_door = ''
time_of_last_unlock = time.time() - 60 # starts @ 1 min ago to lock instantly

# define pins
LOCK_OUTPUT = 36
LOCK_INPUT = 16
DOOR_CIRCUIT = 15

GPIO.setup(LOCK_OUTPUT, GPIO.OUT)
GPIO.setup(LOCK_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DOOR_CIRCUIT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# GETTERS
def IsDoorLocked() -> bool:
    '''
        0 -> electromagnet off -> door unlocked -> false == bool(0)
        1 -> electromagnet on -> door locked -> true == bool(1)
    '''
    val = bool(GPIO.input(LOCK_INPUT))
    colors.print_color("[OUTPUT] Is door locked? %b" % b, "log")
    return val

def IsDoorClosed() -> bool:
    '''
        1 = input high -> circuit unbroken -> door closed
        0 = input low -> circuit broken -> door open
    '''

    return bool(GPIO.input(DOOR_CIRCUIT))

def IsDoorOpen():
    return not bool(IsDoorClosed())

# business logic
def ClosePins():
    GPIO.cleanup()
    
def LockDoor():
    GPIO.output(LOCK_OUTPUT, GPIO.HIGH)
    colors.print_color("[LOCKED] Drawer locked successfully.", "success")

def UnlockDoor():
    global time_of_last_unlock
    time_of_last_unlock = time.time()
    GPIO.output(LOCK_OUTPUT, GPIO.LOW)
    colors.print_color("[UNLOCK] Drawer unlocked successfully.", "success")

def WaitForDoorToOpen():
    if IsDoorOpen():
        return True
    
    while True:
        # use interrupt not to fry CPU
        # GPIO.wait_for_edge(DOOR_CIRCUIT, GPIO.FALLING)

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
        # use interrupt not to fry CPU
        # GPIO.wait_for_edge(DOOR_CIRCUIT, GPIO.RISING)

        # use polling to check if door is open 10x to ensure falling edge was not an accident
        times_detected_true = 0
        while times_detected_true < 10:
            time.sleep(0.3)
            if IsDoorClosed():
                times_detected_true += 1
            else:
                times_detected_true = 0 
    
        return True

def LockDoorEvery60Sec():
    colors.print_color("[LOCKED] Security Measure - Attempting to lock drawer every 60 seconds.", "warning")
    if IsDoorClosed() and time.time() > 60 + time_of_last_unlock:
        LockDoor()

    threading.Timer(60.0, LockDoorEvery60Sec).start()

LockDoorEvery60Sec()
