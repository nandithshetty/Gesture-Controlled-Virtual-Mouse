import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import Gesture_Controller
import app
from threading import Thread
from queue import Queue
import pyaudio
import random


# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files = []
path = ''
is_awake = True  # Bot status
voice_queue = Queue()  # Thread-safe queue for background voice commands
current_mic_index = None
mic_changed = False

# ------------------Exposed Functions--------------
@app.eel.expose
def getMicrophones():
    try:
        p = pyaudio.PyAudio()
        mics = []
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            dev_info = p.get_device_info_by_host_api_device_index(0, i)
            if dev_info.get('maxInputChannels') > 0:
                mics.append({
                    "index": i,
                    "name": dev_info.get('name')
                })
        p.terminate()
        return mics
    except Exception as e:
        print("Error listing mics:", e)
        return []

@app.eel.expose
def setMicrophone(index):
    global current_mic_index, mic_changed
    if index == "":
        current_mic_index = None
        print("Switching microphone to Default...")
    else:
        current_mic_index = int(index)
        print(f"Switching microphone to index {current_mic_index}...")
    mic_changed = True

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(audio)
    try:
        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        print("TTS Engine error:", e)


def wish():
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
        
    reply("I am Max, how may I help you?")


# Audio to String (Runs in background thread)
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        try:
            # Short listen timeout and phrase limit to keep the thread highly responsive
            audio = r.listen(source, timeout=3, phrase_time_limit=4)
            voice_data = r.recognize_google(audio)
        except sr.WaitTimeoutError:
            pass
        except sr.RequestError:
            print("Google Speech API is unavailable")
        except sr.UnknownValueError:
            pass
        except Exception as e:
            # Handle case where microphone is disconnected or disabled
            print("Microphone access exception:", e)
            time.sleep(2.0)
            
        return voice_data.lower()


# Background voice thread worker - listens continuously and supports hot-swapping mics
def voice_listener_worker():
    global is_awake, mic_changed, current_mic_index
    
    while True:
        if not app.ChatBot.started:
            break
            
        mic_changed = False
        device_idx = current_mic_index
        
        try:
            with sr.Microphone(device_index=device_idx) as source:
                print(f"Opening microphone device index: {device_idx if device_idx is not None else 'Default'}")
                # Set a safe, standard static threshold of 300 to prevent startup calibration lock-ups (e.g. from speakers or echo)
                r.energy_threshold = 300
                r.dynamic_energy_threshold = True
                r.dynamic_energy_adjustment_damping = 0.15
                r.dynamic_energy_ratio = 1.5
                r.pause_threshold = 0.8
                print("Microphone initialized with standard dynamic sensitivity.")
                
                # Report mic status to user via UI
                app.ChatBot.addAppMsg("Microphone activated! Standard sensitivity calibrated.")
                
                while not mic_changed:
                    if not app.ChatBot.started:
                        break
                    try:
                        # Blocks cleanly in the background thread waiting for speech
                        audio = r.listen(source, phrase_time_limit=5)
                        voice_data = r.recognize_google(audio)
                        if voice_data:
                            voice_data = voice_data.lower()
                            print("Background recognized voice:", voice_data)
                            voice_queue.put(voice_data)
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError:
                        print("Google Speech API request error")
                    except Exception as e:
                        print("Error during speech recognition loop:", e)
                        time.sleep(0.5)
        except Exception as e:
            print(f"Failed to open microphone index {device_idx}:", e)
            app.ChatBot.addAppMsg(f"Failed to connect to selected microphone index {device_idx}. Please select another.")
            time.sleep(2.0)


# Executes Commands (input: clean lowercase string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print("Executing command:", voice_data)
    
    # GUI messages are added directly, for voice we add here
    # Check if the message is already in the UI. If not, add it.
    # (GUI inputs are already added in main loop before calling respond)

    # STATIC CONTROLS
    if 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Max!')

    elif 'date' in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif 'time' in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    elif 'search' in voice_data:
        search_query = voice_data.split('search')[1].strip()
        reply('Searching for ' + search_query)
        url = 'https://google.com/search?q=' + search_query
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif 'location' in voice_data:
        words = voice_data.split('location')
        if len(words) > 1 and words[1].strip():
            place = words[1].strip()
            reply('Locating ' + place + '...')
            url = 'https://google.nl/maps/place/' + place + '/&amp;'
            try:
                webbrowser.get().open(url)
                reply('This is what I found Sir')
            except:
                reply('Please check your Internet')
        else:
            reply('Please specify the location name, for example: location Paris.')

    elif ('bye' in voice_data) or ('by' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False

    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        sys.exit()
        
    # Siri/Alexa Conversational Skills
    elif 'joke' in voice_data:
        jokes = [
            "Why do programmers wear glasses? Because they can't C sharp!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "What is a programmer's favorite hangout place? Foo Bar!",
            "Why did the programmer quit his job? Because he didn't get arrays!",
            "There are 10 types of people in the world: those who understand binary, and those who don't.",
            "Why do Java programmers have to wear glasses? Because they don't C#!"
        ]
        reply(random.choice(jokes))

    elif 'flip a coin' in voice_data or 'toss a coin' in voice_data or 'flip coin' in voice_data:
        outcome = random.choice(['Heads', 'Tails'])
        reply(f"It's {outcome}!")

    elif 'weather' in voice_data:
        responses = [
            "It looks like a wonderful day outside with clear skies and a pleasant breeze.",
            "Expect warm sunshine today, perfect weather for working on virtual mouse major projects!",
            "Currently, the weather is clear and temperate, with comfortable indoor temperatures."
        ]
        reply(random.choice(responses))
        
    # DYNAMIC CONTROLS
    elif any(cmd in voice_data for cmd in ['launch gesture recognition', 'launch gesture controller', 'open gesture controller', 'start gesture controller', 'run gesture controller', 'start gesture recognition', 'open gesture recognition']):
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target = gc.start)
            t.start()
            reply('Launched Successfully')

    elif any(cmd in voice_data for cmd in ['stop gesture recognition', 'stop gesture controller', 'close gesture controller', 'turn off gesture controller', 'turn off gesture recognition', 'top gesture recognition']):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')
        
    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied')
          
    elif 'page' in voice_data or 'pest' in voice_data or 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted')
        
    # File Navigation (Default Folder set to C://)
    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        try:
            files = listdir(path)
            filestr = ""
            for f in files:
                counter += 1
                filestr += str(counter) + ':  ' + f + '<br>'
            file_exp_status = True
            reply('These are the files in your root directory')
            app.ChatBot.addAppMsg(filestr)
        except Exception as e:
            reply('Error accessing root directory')
            print(e)
        
    elif file_exp_status == True:
        counter = 0   
        if 'open' in voice_data:
            try:
                selected_num = int(voice_data.split(' ')[-1])
                target_file = files[selected_num - 1]
                full_path = join(path, target_file)
                if isfile(full_path):
                    os.startfile(full_path)
                    file_exp_status = False
                    reply('Opened Successfully')
                else:
                    path = path + target_file + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter += 1
                        filestr += str(counter) + ':  ' + f + '<br>'
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)
            except Exception as e:
                reply('Could not open folder or file')
                print(e)
                                    
        if 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory')
            else:
                try:
                    a = path.split('//')[:-2]
                    path = '//'.join(a)
                    path += '//'
                    files = listdir(path)
                    for f in files:
                        counter += 1
                        filestr += str(counter) + ':  ' + f + '<br>'
                    reply('Moved back')
                    app.ChatBot.addAppMsg(filestr)
                except Exception as e:
                    reply('Error navigating back')
                    print(e)
                   
    else: 
        reply('I am not functioned to do this!')


# ------------------Driver Code--------------------

t1 = Thread(target = app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()

# Start background microphone voice listener thread
voice_thread = Thread(target=voice_listener_worker)
voice_thread.daemon = True
voice_thread.start()

# Helper to match phonetic variations of the wake word "Max"
def check_wake_word(voice_data):
    wake_words = ['max', 'macs', 'makes', 'mack']
    for word in wake_words:
        if word in voice_data:
            return True, word
    return False, None

# Non-blocking unified polling loop
while True:
    if not app.ChatBot.started:
        break

    # 1. Check & Process GUI Input (Instant responses, no wake word prefix required)
    if app.ChatBot.isUserInput():
        raw_msg = app.ChatBot.popUserInput()
        # Clean text
        clean_msg = raw_msg.lower()
        has_wake, matched_word = check_wake_word(clean_msg)
        if has_wake:
            clean_msg = clean_msg.replace(matched_word, '').strip()
        else:
            clean_msg = clean_msg.strip()
        
        # Display typed text on UI
        app.eel.addUserMsg(raw_msg)
        
        # Wake up if text is typed
        if not is_awake:
            is_awake = True
            
        try:
            respond(clean_msg)
        except SystemExit:
            break
        except Exception as e:
            print("Error executing GUI command:", e)

    # 2. Check & Process Voice Input (Wake word 'max' is optional)
    if not voice_queue.empty():
        voice_data = voice_queue.get()
        print("Heard voice:", voice_data)
        
        if is_awake:
            # Wake word 'max' is optional! If present, we strip it.
            has_wake, matched_word = check_wake_word(voice_data)
            if has_wake:
                clean_voice = voice_data.replace(matched_word, '').strip()
            else:
                clean_voice = voice_data.strip()
                
            # Display voice text in UI
            app.eel.addUserMsg(voice_data)
            
            try:
                respond(clean_voice)
            except SystemExit:
                break
            except Exception as e:
                print("Error executing voice command:", e)
        else:
            # If system is asleep, only waking up is supported
            has_wake, matched_word = check_wake_word(voice_data)
            clean_voice = voice_data.replace(matched_word, '').strip() if has_wake else voice_data.strip()
            if 'wake up' in clean_voice or 'wake up' in voice_data:
                app.eel.addUserMsg(voice_data)
                is_awake = True
                wish()
                
    time.sleep(0.05)  # Light polling sleep (50ms) to conserve CPU
