import json
import requests

import pip
try:
    import keyboard
    import speech_recognition as sr
    import pyttsx3
except ImportError:
    pip.main(['install', 'keyboard'])
    pip.main(['install', 'speech_recognition'])
    pip.main(['install', 'pyttsx3'])
    import keyboard
    import speech_recognition as sr
    import pyttsx3

v_Recognition = ""  

r = sr.Recognizer()
ttsEngine = pyttsx3.init()

def sayPrice(name, price):
    voiceLine = 'The price of %s is %.0f'%(name, price)

    print('voiceLine')
    ttsEngine.say(voiceLine)
    ttsEngine.runAndWait()

while True:
    if keyboard.is_pressed('caps lock'):
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            v_Recognition = str(r.recognize_google(audio))

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    
        def run_query(query):
            print ('running query')
            response = requests.post('https://api.tarkov.dev/graphql', json={'query': query})
            if response.status_code == 200:
                data = response.text
                parse_json = json.loads(data)
                
                if len(parse_json['data']['items']) == 0:
                    ttsEngine.say('Item not found')
                    ttsEngine.runAndWait()
                    return

                items = parse_json['data']['items'][0]
                
                avg24hPrice = items['avg24hPrice']
                basePrice = items['basePrice']
                name = items['name']
                
                if avg24hPrice == 0:
                    sayPrice(name, basePrice)
                else:
                    if avg24hPrice < basePrice:
                        sayPrice(name, basePrice)
                    else:
                        sayPrice(name, avg24hPrice)
                
                

                return response.json()
            
            else:
                raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))  
        new_query = """
    {
        items(name: "%s") {
            basePrice
            avg24hPrice
            name
            shortName
        }
    }
    """ % v_Recognition
        
        run_query(new_query)
