import FiniteStateMachine as FSM
import globals as gb

def main():   
    # begin Finite State Machine
    try:
        FSM.FSM(FSM.STATES.reset)

    except BaseException as e:
        gb.reader.ClosePort()
        print("exception thrown", str(e))

if ( __name__ == "__main__"):
    main()
    # GPIO.cleanup()