import json
import requests
import pip
import sqlite3
import datetime
try:
    import keyboard
    import speech_recognition as sr
    import pyttsx3
    from thefuzz import fuzz, process
except ImportError:
    pip.main(['install', 'keyboard'])
    pip.main(['install', 'speech_recognition'])
    pip.main(['install', 'pyttsx3'])
    pip.main(['install', 'thefuzz'])
    import keyboard
    import speech_recognition as sr
    import pyttsx3
    from thefuzz import fuzz, process

# Create and connect to SQLite database
conn = sqlite3.connect('tarkov_data.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS item_data
             (name TEXT, base_price REAL, avg_24h_price REAL)''')

# Commit the changes and close the connection
conn.commit()

v_Recognition = ""
r = sr.Recognizer()
ttsEngine = pyttsx3.init()

# Text to Speech to tell the user the price of the item
def sayPrice(name, price):
    voiceLine = 'The price of %s is %.0f' % (name, price)
    ttsEngine.say(voiceLine)
    ttsEngine.runAndWait()

# Save item data to the SQLite database
def save_item_data(name, base_price, avg_24h_price):
    c.execute("INSERT INTO item_data (name, base_price, avg_24h_price) VALUES (?, ?, ?)",
              (name, base_price, avg_24h_price))
    conn.commit()

def get_all_items_from_database():
    c.execute("SELECT name, base_price, avg_24h_price FROM item_data")
    results = c.fetchall()
    return results    

def get_item_from_database(item_name):
    items = get_all_items_from_database()
    best_match = process.extractOne(item_name, items, scorer=fuzz.token_set_ratio) [0][0]
    print(best_match)
    c.execute("SELECT name, base_price, avg_24h_price FROM item_data WHERE name = ?", (best_match,))
    result = c.fetchone()
    return result


# Function to fetch all items from the API and store them in the local database
def fetch_and_store_all_items():
    query = """
    {
        items {
            basePrice
            avg24hPrice
            name
            shortName
        }
    }
    """

    print('Fetching all items from the API...')
    response = requests.post('https://api.tarkov.dev/graphql', json={'query': query})

    if response.status_code == 200:
        data = response.text
        parse_json = json.loads(data)
        items = parse_json['data']['items']

        for item in items:
            name = item['name']
            base_price = item['basePrice']
            avg_24h_price = item['avg24hPrice']

            # Save item data to the SQLite database
            save_item_data(name, base_price, avg_24h_price)

        print('All items have been fetched and stored in the local database.')

    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))            

def get_last_fetch_time():
    with open("last_fetch.txt", "r") as file:
        last_fetch_str = file.read()
        last_fetch_time = datetime.datetime.strptime(last_fetch_str, "%Y-%m-%d %H:%M:%S")
    return last_fetch_time

def update_last_fetch_time():
    now = datetime.datetime.now()
    with open("last_fetch.txt", "w") as file:
        file.write(now.strftime("%Y-%m-%d %H:%M:%S"))

def should_fetch_items():
    try:
        last_fetch_time = get_last_fetch_time()
    except FileNotFoundError:
        return True

    now = datetime.datetime.now()
    time_since_last_fetch = now - last_fetch_time
    return time_since_last_fetch > datetime.timedelta(hours=48) # Database update time

if should_fetch_items():
    fetch_and_store_all_items()
    update_last_fetch_time()
    print("Items fetched and stored.")

# Checks if the hotkey is held down
while True:
    if keyboard.is_pressed('caps lock'):
        with sr.Microphone() as source:
            audio = r.listen(source)
        try:
            v_Recognition = str(r.recognize_google(audio, show_all=False))

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from speech recognition service")
                # Check if the item data is already in the database
        item_data = get_item_from_database(v_Recognition)

        if item_data:
            name, base_price, avg_24h_price = item_data
            if avg_24h_price == 0:
                sayPrice(name, base_price)
            else:
                if avg_24h_price < base_price:
                    sayPrice(name, base_price)
                else:
                    sayPrice(name, avg_24h_price)

        else:
            print("Item not found in local database")

