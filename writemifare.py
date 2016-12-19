# Example of detecting and reading a block from a MiFare NFC card.
# Author: Manuel Fernando Galindo (mfg90@live.com)
#
# Copyright (c) 2016 Manuel Fernando Galindo
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import binascii
import sys
import array
import PN532


CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]


# Create an instance of the PN532 class.
pn532 = PN532.PN532("/dev/ttyUSB0",115200)
pn532.begin()
pn532.SAM_configuration()

# Get the firmware version from the chip and print(it out.)
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Step 1, wait for card to be present.
print('Mifare NFC Writer')
print('')
print('== STEP 1 =========================')
print('Place the card to be written on the PN532...')
uid = pn532.read_passive_target()
while uid is "no_card":
    uid = pn532.read_passive_target()
print('')
print('Found card with UID: 0x{0}'.format(binascii.hexlify(uid)))
print('')
print('==============================================================')
print('WARNING: DO NOT REMOVE CARD FROM PN532 UNTIL FINISHED WRITING!')
print('==============================================================')
print('')

# Step 2, pick a block type.
print('== STEP 2 =========================')
print('Now pick a block type to write to the card.')
status = False
block_choice=0
while not status:
    print('')
    print('Type either L to list block types, or type the number of the desired block.')
    print('')
    choice = input('Enter choice: ')
    print('')

    try:
        block_choice = int(choice)
        if not (choice in range(4,16)):
            print('Error! Unrecognized block')
        else:
            status = True
    except ValueError:
        # Something other than a number was entered.  Try again.
        print('Error! Unrecognized option.')
        continue

status = False
block_info = None
while not status:
    print('')
    print('Type the value to write on block (16 bytes).')
    print('')
    choice = raw_input('Enter: ')
    print('')

    data = bytearray(16)
    if(len(choice)<=16):
        for i in range(0, len(choice)):
            data[i]=choice[i]

    block_info = data
    print "Info:"+str(block_info)+" size:"+str(len(block_info))

    if(block_info is not None):
        status=True


# Confirm writing the block type.
print('== STEP 3 =========================')
print('Confirm you are ready to write to the card:')
print ("Block: "+str(block_choice))
choice = raw_input('Confirm card write (Y or N)? ')
if choice.lower() != 'y' and choice.lower() != 'yes':
    print('Aborted!')
    sys.exit(0)
print('Writing card (DO NOT REMOVE CARD FROM PN532)...')

# Write the card!
# First authenticate block 4.
if not pn532.mifare_classic_authenticate_block(uid, block_choice, PN532.MIFARE_CMD_AUTH_B,
                                               CARD_KEY):
    print('Error! Failed to authenticate block 4 with the card.')
    sys.exit(-1)
# Next build the data to write to the card.
# Format is as follows:
# - Bytes 0-3 are a header with ASCII value 'MCPI'
# - Byte 4 is the block ID byte
# - Byte 5 is 0 if block has no subtype or 1 if block has a subtype
# - Byte 6 is the subtype byte (optional, only if byte 5 is 1)

# Finally write the card.
if not pn532.mifare_classic_write_block(block_choice, block_info):
    print('Error! Failed to write to the card.')
    sys.exit(-1)
print('Wrote card successfully! You may now remove the card from the PN532.')
