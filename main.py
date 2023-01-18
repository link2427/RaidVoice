import asyncio
import json
import keyboard
import time
import requests
import speech_recognition as sr



r = sr.Recognizer()

while True:
    if keyboard.is_pressed('caps lock'):
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            print("You said: " + r.recognize_google(audio))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

 
def run_query(query):
    print ('running query')
    response = requests.post('https://api.tarkov.dev/graphql', json={'query': query})
    if response.status_code == 200:
        print (response.json)
        return response.json()
    
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))


