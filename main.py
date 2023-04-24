import FiniteStateMachine as FSM
import globals as gb
import GPIO as gpio

def main():   
    # begin Finite State Machine
    try:
        FSM.FSM(FSM.STATES.reset)

    except BaseException as e:
        gb.reader.ClosePort()
        print("[ERROR] Exception thrown: ", str(e))

if ( __name__ == "__main__"):
    main()
    gpio.ClosePins()