import json
import keyboard
import requests
import speech_recognition as sr

v_Recognition = ""

r = sr.Recognizer()

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
                items = parse_json['data']['items'][0]
                avg24hPrice = parse_json['data']['items'][0]['avg24hPrice']
                basePrice = parse_json['data']['items'][0]['basePrice'] 
                name = parse_json['data']['items'][0]['name']
                
                if avg24hPrice == 0:
                    print(basePrice)
                else:
                    print(avg24hPrice)
                
                
                #print(response.json())
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
