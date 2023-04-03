# flipper-wiegand-encryptor
## Description
A tool to generate encrypted wiegand block for HID Corporate 1000 35-bit iClass cards. Can also generate .picopass files to be used with the Flipper Zero.

## Usage
```
❯ python3 encrypt.py -h
usage: encrypt.py [-h] --fc FC --cn CN [-n NAME]

DESCRIPTION: Generate encrypted wiegand block for HID Corporate 1000 35-bit iClass cards. Can also generate .picopass files to
be used with the Flipper Zero

options:
  -h, --help            show this help message and exit
  --fc FC               facility code, usually an integer between 0 and 4095. Will most likely be common amongst all cards in
                        the campus.
  --cn CN               card number, usually an integer between 1 and 1048575. Unique to each card and will be printed on the
                        back.
  -n NAME, --name NAME  the name or title of the badge owner (ex. 'john' or 'manager'). This name will be used to name the
                        output file
```

## Installing necessary libraries
1. Ensure you have python3 and pip installed on your system.
2. Install the libraries in requirements.txt
  `python3 -m pip install -r requirements.txt`

## How to run
Let's say the card you want to clone has a facility code of 1337 and the card number is 69420. To get the plain and encrypted Wiegand block, you would run the following:
```
❯ python3 encrypt.py --fc 1337 --cn 69420
[+] FC.......... 1337
[+] card num.... 69420
[+] plaintext... 00000008A7221E59
[+] encrypted... B0E2A6F8644CA2CC
```
If you want this to then be saved to a `.picopass` file to be used with the Flipper Zero, add the `-n/--name` flag to give the output file a name. For example, let's say the badge belongs to "Dade Murphy" and has the same facility code and card number as before. Run the following command:
```
❯ python3 encrypt.py --fc 1337 --cn 69420 --name dadeMurphy
[+] FC.......... 1337
[+] card num.... 69420
[+] plaintext... 00000008A7221E59
[+] encrypted... B0E2A6F8644CA2CC
Saved output to dadeMurphy.picopass. Copy this file to apps_data/picopass directly using the SD card or via the qflipper app.
```
