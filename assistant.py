import speech_recognition as sr, pyttsx3, time

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

####################################################################

def record_text():
    try:
        with m as source: 
            print("Listening...")
            audio = r.listen(source)
        print("Got it! Now to recognize it...")
        
        # recognize speech using Google Speech Recognition
        value = r.recognize_google(audio)

        print("You said {}".format(value))

        return value
        
    except sr.UnknownValueError:
        print("Oops! Didn't catch that")
    except sr.RequestError as e:
        print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
    except KeyboardInterrupt:
        pass

def speak(sentence_string):
    # Convert text to speech
    engine.say(str(sentence_string))

    # Wait for the speech to finish
    engine.runAndWait()

def onStart(name, location, length):
    if location == 0:
        print('Loading speech...')
        time.sleep(1.5)

while(active):
    text = record_text()

    # Special cases
    if text == None:
        continue
    if ("end" in text) or ("terminate" in text) or ("quit" in text) or ("kill" in text):
        active = False
        break

    print("Wrote text: "+ text)
    engine.connect('started-word', onStart)

    # Filler function used to verify speach-to-text accuracy
    speak(text)