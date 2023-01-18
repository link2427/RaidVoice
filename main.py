import websockets
import asyncio
import base64
import json
import pyaudio
import keyboard
import time
import config
import requests
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
auth_key = config.auth_key

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000


p = pyaudio.PyAudio()
stream = p.open(
   frames_per_buffer=FRAMES_PER_BUFFER,
   rate=SAMPLE_RATE,
   format=pyaudio.paInt16,
   channels=1,
   input=True,
)

def run_query(query):
    print ('running query')
    response = requests.post('https://api.tarkov.dev/graphql', json={'query': query})
    if response.status_code == 200:
        parse_json = response.json()
        res = parse_json['data']['items'][0]['avg24hPrice']
        print(res)
        return res
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

stop_event = asyncio.Event()

async def send_receive():
   print(f'Connecting websocket to url ${URL}')
   async with websockets.connect(
       URL,
       extra_headers=(("Authorization", auth_key),),
       ping_interval=5,
       ping_timeout=20
   ) as _ws:
       await asyncio.sleep(0.1)
       print("Receiving SessionBegins ...")
       session_begins = await _ws.recv()
       print(session_begins)
       print("Sending messages ...")
       async def send():
           while True:
               if stop_event.is_set():
                   break
               try:
                   data = stream.read(FRAMES_PER_BUFFER)
                   data = base64.b64encode(data).decode("utf-8")
                   json_data = json.dumps({"audio_data":str(data)})
                   await _ws.send(json_data)
               except websockets.exceptions.ConnectionClosedError as e:
                   print(e)
                   assert e.code == 4008
                   break
               except Exception as e:
                   assert False, "Not a websocket 4008 error"
               await asyncio.sleep(0.01)
          
           return True
      
       async def receive():
           while True:
               if stop_event.is_set():
                   break
               try:
                   result_str = await _ws.recv()
                   print(json.loads(result_str)['text'])    
                   new_query = """
                    {
                        items(name: "%s") {
                            avg24hPrice
                        }
                    }""" % result_str
                    
            
               except websockets.exceptions.ConnectionClosedError as e:
                   print(e)
                   assert e.code == 4008
                   break
               except Exception as e:
                   assert False, "Not a websocket 4008 error"
               print(run_query(new_query))
               # print the avg 24 hr price here
               
               
       send_result, receive_result = await asyncio.gather(send(), receive())

async def background_task():
    task = asyncio.create_task(send_receive())
    await asyncio.sleep(6) # run the task for 6 secs
    task.cancel()
# Checking for keyboard input
while True:
    if keyboard.is_pressed('capslock'):
        asyncio.run(background_task())
    time.sleep(0.1)



