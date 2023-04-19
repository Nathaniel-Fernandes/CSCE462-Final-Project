import time
# import RPi.GPIO as GPIO
import j421xlib

# GPIO.setmode(GPIO.BOARD)
# GPIO.setwarnings(False)

def Test():
    # load the library
    f = j421xlib.J4210()
    ver = f.LibVersion()

    print("Lib Version: ", ver)
    print('Last Error: ', f.LastError())

    # Get & Connect to a port
    ports = f.AvailablePorts()
    print("Available Serial Ports:", ports)
    f.OpenPort(ports[1], 57600)

    reader_info = f.LoadSettings()
    reader_info.echo()

    # change power
    # print("Saving modified settings:")
    try:
        reader_info.Power = 19
        f.SaveSettings(reader_info)
        f.LoadSettings().echo()
    except:
        print("Could not save reader settings")

    # Perform inventory scan
    while True:
        f.SetQ(5) # Q is 0 to 15 
        n = f.Inventory(False)

        print("Tags found: ", n)
        time.sleep(5)

    # # list inventory
    # print("Tag List:")
    # for i in range(n):
    #     sr = f.GetResult(i)
    #     #sr.echo()
    #     sr.line()

    # # get TID
    # if (n > 0):
    #     sr = f.GetResult(0) # get TID of first tag
    #     # check if the tag exist
    #     found = f.TagExists(sr.EPC)
    #     taginfo = None
    #     if (found):
    #         print("Tag FOUND!")
    #         tid = f.GetTID(sr.EPC)
    #         print("TID: ", f.Bytes2Hex(tid), " EPC: ", f.Bytes2Hex(sr.EPC))

    #         # get details of the Tag
    #         print("Getting Tag Info for this tag:")
    #         taginfo = f.GetTagInfo(tid)
    #         taginfo.echo()
    #     else:
    #         print("Tag with EPC ", f.Bytes2Hex(sr.EPC), " not found.")

    #     # we will set the password now
    #     # if you know the tags password, set it here
    #     # this is the default password (size 4 byte)
    #     password = b'\x00\x00\x00\x00' 
    #     ret = f.Auth(password)
    #     assert ret == True

    #     # we will change the password
    #     # set a new password here. We used the default password
    #     # to keep the password unchange and showing you how to 
    #     # change the password, if you need to.
    #     # NOTE: You must first set the old password using the Auto
    #     # method. If you do not call it, the default password will
    #     # automatically be used.
    #     newpass =  b'\x00\x00\x00\x00'
    #     #ret = f.SetPassword(sr.EPC, newpass)
    #     #assert ret == True

    #     if (taginfo.userlen > 0):
    #         # write something to user memory
    #         data = b'\xFE\xED'
    #         print("Data to be written: ", f.Bytes2Hex(data))
    #         ret = f.WriteMemWord(sr.EPC, data, 0)
    #         assert ret == True

    #         # now read it back
    #         data2 = f.ReadMemWord(sr.EPC, 0)
    #         assert data2 != None
    #         print("Data Read: ",f.Bytes2Hex(data2))
    #         assert data == data2

    #     else:
    #         # this tag does not have user memory
    #         print("This tag does not have user memory")
        
    #     # change EPC word
    #     # EPC is change 16-bit (2 bytes) at a time.
    #     # EPC is usually 12 byte, so to change the EPC
    #     # you need to write 6 times where the index will
    #     # be supplied from 0 to 5
    #     print("Current EPC = ", f.Bytes2Hex(sr.EPC))
    #     newepc0 = b'\xba\xba'
    #     print("Changing the EPC first two bytes to ", f.Bytes2Hex(newepc0))
    #     # our first index is 0
    #     ret = f.WriteEpcWord(sr.EPC, newepc0, 0)
    #     assert ret == True
    #     # because our EPC has changed, we need to modify the EPC as well
    #     epc = newepc0 + sr.EPC[2:]
    #     print("The new EPC is now ", f.Bytes2Hex(epc))
    #     newepc1 = b'\xda\xda'
    #     print("Changing the EPC second two bytes to ", f.Bytes2Hex(newepc1))
    #     ret = f.WriteEpcWord(epc, newepc1, 1)
    #     assert ret == True
    #     # repeat this for index 2 through 5 to change the whole EPC
    #     epc = epc[0:2] + newepc1 + sr.EPC[4:]
    #     print("Thew new EPC is now ", f.Bytes2Hex(epc))

    #     # we will now use filter to find out how many tag starts with babadada
    #     adr = 0 # mask addres is in byte but on word (2 byte) boundry
    #     masklen = 4 # mask length is in byte
    #     mask = b'\xba\xba\xda\xda'
    #     ret = f.SetFilter(adr, masklen, mask)
    #     assert ret == True
    #     # now perform inventory using the filter
    #     n = f.Inventory(True) # passing True tells to use the filter
    #     assert n > 0, "Inventory count returned ZERO!"
    #     # list inventory
    #     print("Tag List:")
    #     for i in range(n):
    #         sr = f.GetResult(i)
    #         #sr.echo()
    #         sr.line()

    # # Here GPIO tests are done. If you have the hardware with GPIO
    # # you can run this test to turn on LEDs at the GPIO ports.
    # print("Setting GPO-0 and GPO-1 to 1")
    # f.SetGPO(3)
    # print("GPI-0 = ", f.GetGPI(1))
    # print("GPI-1 = ", f.GetGPI(2))


    # close connection
    f.ClosePort()

    print("DONE!")

Test()

def main():
    pass

# if ( __name__ == "__main__"):
#     main()
#     GPIO.cleanup()