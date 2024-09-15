import serial
import time

# Open the serial connection (adjust the port as needed)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Allow some time for the connection to establish
time.sleep(2)

print('connected:', ser)

def sendAttackSignal():
	# Send a message to the Arduino
	ser.write(b'1')
	time.sleep(5)
	ser.write(b'0')

# Main loop
while True:
	notVerified = True
	if notVerified:
		print("triggered attack!")
		sendAttackSignal()
	else:
		print("no attack")
	time.sleep(5)

