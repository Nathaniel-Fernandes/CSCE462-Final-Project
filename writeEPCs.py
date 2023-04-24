import helpers

# connect reader, perform scan
f = helpers.SetupReader()
f.Inventory(False)
sr = f.GetResult(0)
print(f.Bytes2Hex(sr.EPC))


# EPC is change 16-bit (2 bytes) at a time.
# EPC is usually 12 byte, so to change the EPC
# you need to write 6 times where the index will
# be supplied from 0 to 5
def changeEPC(target_epc, curr_epc, i):
    ''' Recursively changes current EPC 2 bytes at a time'''
    if i >= 6:
        return
    
    ret = f.WriteEpcWord(curr_epc, target_epc[2*i:2*(i+1)], i)
    assert ret == True

    # change word for next time
    updated_epc = list(curr_epc)
    updated_epc[2*i:2*(i+1)] = list(target_epc)[2*i:2*(i+1)]
    updated_epc = bytes(updated_epc)

    return changeEPC(target_epc, updated_epc, i+1)

# change EPC word
currepc = sr.EPC

newepc = b'\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22'
# changeEPC(newepc, currepc, 0)

# check if tag has been changed
f.Inventory(False)
sr = f.GetResult(0)
print(f.Bytes2Hex(sr.EPC))

f.ClosePort()

# Copy and paste
# b'\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
# b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
