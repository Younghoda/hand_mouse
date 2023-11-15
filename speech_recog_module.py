# pip install SpeechRecognition
import speech_recognition as sr
from queue import Queue

def speech_recognition_thread(queue):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            audio = r.listen(source)
            try:
                command = r.recognize_google(audio)
                queue.put(command.lower())
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                pass