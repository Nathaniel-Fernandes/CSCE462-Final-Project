import sys
import FiniteStateMachine as FSM
import globals as gb
import GPIO as gpio
import colors

def main():   
    if len(sys.argv) < 2:
        raise RuntimeError("Must input the cabinet id")
    
    # set global cabinet id
    gb.cabinet_id = sys.argv[1]

    # begin Finite State Machine
    try:
        FSM.FSM(FSM.STATES.reset)

    except BaseException as e:
        gb.reader.ClosePort()
        colors.print_color("[ERROR] Exception thrown: %s" % str(e), "error")

if ( __name__ == "__main__"):
    main()
    gpio.ClosePins()