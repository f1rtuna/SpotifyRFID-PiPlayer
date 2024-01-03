import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

reader = SimpleMFRC522()

try:
    while True:
        embeddedLink = input("place embedded link from spotify or -1 to exit quit: ")
        if embeddedLink == "-1":
            break
        fullTrack = embeddedLink.split("/")[-1]
        trackId = fullTrack.split("?")[0].strip()
        print("track id for you song is: ", trackId)
        print("place card on reader")
        reader.write(trackId)
        id, songId = reader.read()
        print("track id for card written to RFID reader")

        
except Exception as e:
    print(e)
    GPIO.cleanup()
    print("GPIO good to go")
