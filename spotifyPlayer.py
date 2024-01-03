import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
from queue import Queue
from dotenv import load_dotenv
import os
reader = SimpleMFRC522()

pausePin = 40
playPin = 38

pausePrev = None
playPrev = None

load_dotenv()
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
DEVICE_ID = os.getenv("SPOTIFY_DEVICE_ID")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = CLIENT_ID,
                                                   client_secret = CLIENT_SECRET,
                                                   redirect_uri="http://localhost:8080",
                                                   scope="user-read-playback-state,user-modify-playback-state"))
# pplace commands here
command_queue = Queue()

def card_reader():
    while running:
        id, songId = reader.read()
        print("ID: ", id)
        print("SongId: ", songId)
        
        # Handle card information
        if id is not None:
            track = 'spotify:track:' + str(songId.strip())
            print("playing: ", track)
            #command_queue.put(("begin_playback", "spotify:track:2WEWR2rxDnSY2XIQwWAUSe"))
            command_queue.put(("begin_playback", track))
        time.sleep(2)

def playback_controller():
    pausePrev = 0
    playPrev = 0

    while running:
        pauseVal = GPIO.input(pausePin)
        playVal = GPIO.input(playPin)

        if pauseVal == 0 and pausePrev == 1:
            command_queue.put("pause_playback")
            time.sleep(0.1)
        if playVal == 0 and playPrev == 1:
            command_queue.put("start_playback")
            time.sleep(0.1)

        pausePrev = pauseVal
        playPrev = playVal
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        sp.transfer_playback(device_id = DEVICE_ID, force_play=False)
        
        # Create threads for card reading and playback control
        card_reader_thread = threading.Thread(target = card_reader, daemon = True)
        playback_controller_thread = threading.Thread(target = playback_controller, daemon = True)
        
        running = True
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pausePin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(playPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        # Start the threads
        card_reader_thread.start()
        playback_controller_thread.start()


        while True:
            command = command_queue.get()
            if len(command) == 2:
                sp.start_playback(device_id = DEVICE_ID, uris=[command[1]])
                #sp.start_playback(device_id=DEVICE_ID, uris=['spotify:track:0Wc6cbF38a90b8wov9V63F'])
            if command == "pause_playback":
                sp.pause_playback(device_id = DEVICE_ID)
            elif command == "start_playback":
                sp.start_playback(device_id = DEVICE_ID)

    except KeyboardInterrupt:
        running = False
        time.sleep(.1)
        # Clean up GPIO and other resources
        card_reader_thread.join(timeout=1)  # Timeout to ensure a clean exit
        playback_controller_thread.join(timeout=1)  # Timeout to ensure a clean exit
        GPIO.cleanup()
        print("GPIO cleaned")

    finally:
        GPIO.cleanup()
