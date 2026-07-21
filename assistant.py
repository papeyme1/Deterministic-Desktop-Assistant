import speech_recognition as sr, pyttsx3, time, importlib
from num2words import num2words
from word2number import w2n

active = True
r = sr.Recognizer()
m = sr.Microphone()

print("A moment of silence, please...")
with m as source: r.adjust_for_ambient_noise(source, 1)
r.energy_threshold += 10
print("Set minimum energy threshold to {}".format(r.energy_threshold))

###################################################################
# Initialize the engine
engine = pyttsx3.init()

# Set properties (optional)
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1.0) # Volume (0.0 to 1.0)

###################################################################

# TTS functions ---------------------------------------------------
def record_text():
    try:
        with m as source: 
            print("Listening...")
            audio = r.listen(source)
        print("Speech detected. Recognizing...")
        
        # recognize speech using Google Speech Recognition
        value = r.recognize_google(audio)
        return value
        
    except sr.UnknownValueError:
        print("Oops! Didn't catch that")
    except sr.RequestError as e:
        print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
    except KeyboardInterrupt:
        pass

def speak(sentence_string):
    print(sentence_string)
    # Convert text to speech
    engine.say(str(sentence_string))

    # Wait for the speech to finish
    engine.runAndWait()

def onStart(name, location, length):
    if location == 0:
        print('Loading speech...')
        time.sleep(1.5)
# -----------------------------------------------------------------

def call_outside_function(executable):
    func = getattr(importlib.import_module("assistant_functions"), executable)
    func()

# Number formatting
def format_number(text, decimal=False):
    text = text.split(" ")
    # EX: one, two, three
    if decimal == False:    
        for index in range(len(text)):
            if (text[index].isdigit()):
                text[index] = num2words(int(text[index]))
    # EX: 1, 2, 3
    else:
        for index in range(len(text)):
            try:
                text[index] = str(w2n.word_to_num(text[index]))
            except ValueError:
                print("ValErr")
            except TypeError:
                print("TypeErr")
    text = " ".join((text))
    return str(text)

attempts = 1
while(active):
    text = record_text()

    # Special cases
    if text == None:
        attempts += 1
        if attempts > 3:
            print("No speech detected. If this doesn't seem right, please check your microphone.")
            break
        continue
    if ("end" in text) or ("terminate" in text) or ("quit" in text) or ("kill" in text):
        active = False
        break

    text = format_number(text, decimal=False)

    # Timeout handling
    attempts = 1
    engine.connect('started-word', onStart)

    print("You said {}".format(text))

    # Handles function calls from user inout
    if ("execute" in text) or ("begin" in text) or ("start" in text) or ("use" in text):
        with open("assistant_functions.py", "r", encoding="utf-8") as file:
            potential_executables = []
            matches = []

            # Grabbing list
            for line in file:
                if "def" in line:
                    potential_executables.append(line[4:(line.find("("))])

            # Function matching       
            for function in potential_executables:
                if function.replace("_", " ") in text:
                    matches.append(function.replace("_", " "))
            
            # Execution handling
            if (len(matches) == 0):
                speak("No executables found with that name.")
            elif (len(matches) == 1):
                speak("Executing " + str(matches))
                call_outside_function(matches[0].replace(" ", "_"))
            else:
                speak("Choose function: " + str(matches))
                num = ""
                for i in range(3):
                    num = record_text()
                    if num != None:
                        break
                    else:
                        print("No speech detected.")
                num = format_number(num, decimal=True).split(" ")
                print("recorded: " + str(num))
                for index in range(len(num)-1):
                    if not num[index].isdigit():
                        num.pop(index)
                num = int("".join(num))
                print("Final: " + str(num))
                if num <= len(matches):
                    call_outside_function(matches[num-1])
                else:
                    speak("Selection outside of range.")