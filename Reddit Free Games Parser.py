"""
todo:
    Create gog tables with all gog games currently in there.
    Create Free games table for keeping track of reddit games we have found
    Create any other games tables and populate them
    connect to server and update free games table and other game tables
    cross check if I have already seen link for game if so don't include in message.
    


"""
import re
import mysql.connector
from mysql.connector import Error
from config import CONFIGURATIONS
import requests
from bs4 import BeautifulSoup
import smtplib
import sys
import logging
from email.message import EmailMessage


CARRIERS = CONFIGURATIONS['carriers']
EMAIL = CONFIGURATIONS['credentials']['email']
PASSWORD = CONFIGURATIONS['credentials']['password']
PHONENUMBER = CONFIGURATIONS['credentials']['phone']
DATABASE = CONFIGURATIONS['database']

def send_message(phone_number, carrier, message):
    msg = EmailMessage()
    msg['Subject'] = f'Free Games Findings'
    msg.set_content(message)
    
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)
 
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])
 
    server.sendmail(auth[0], recipient, message)


def extract_numeric_value(url):
    # Define a regex pattern to match numeric values in the URL
    pattern = re.compile(r'\d+')
    
    # Search for the pattern in the URL
    match = re.search(pattern, url)
    
    # If a match is found, return the numeric value as a string
    if match:
        return match.group()
    else:
        return None  # Return None if no numeric value is found


#pulls url data from html document and creates a set of urls to eliminate duplicates
def parseData(soup,stores):
    htmlResultList = []
    for a in soup.find_all('a', href=True) :
        try:
            link = (a['href'].split('/')[2])
            for store in stores:
                if ((link == store) and ('domain' not in a['href']) ):
                    htmlResultList.append(a['href'])
        except:
            continue
    return [*set(htmlResultList)]


def epicGogQuery(platform, cursor, name, url, connection, messageArray):
    # Check if the combination of Name and URL already exists
    query = f"SELECT * FROM {platform} WHERE Name = %s AND URL = %s"
    cursor.execute(query, (name, url))
    result = cursor.fetchone()

    if result:
        print(f"The game '{name}' already exists in the '{platform}' database.")
    else:
        # Insert the new entry
        insert_query = f"INSERT INTO {platform} (Name, URL) VALUES (%s, %s)"
        cursor.execute(insert_query, (name, url))
        connection.commit()
        print(f"New game '{name}' inserted successfully into '{platform}'.")
        return messageArray.append("""\n""" + name + """\n""" + url + """,\n""")


def steamQuery(platform, cursor, name, url, connection, numeric_value, messageArray):
    # Check if the combination of Name and URL already exists
    query = f"SELECT * FROM {platform} WHERE GameID = %s AND Name = %s AND URL = %s"
    cursor.execute(query, (numeric_value, name, url))
    result = cursor.fetchone()

    if result:
        print(f"The game '{name}' already exists in the '{platform}' database.")
    else:
        # Insert the new entry
        insert_query = f"INSERT INTO {platform} (GameID, Name, URL) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (numeric_value, name, url))
        connection.commit()
        print(f"New game '{name}' inserted successfully into '{platform}'.")
        return messageArray.append("""\n""" + name + """\n""" + url + """,\n""")


def check_and_insert(gameList, messageArray):
    try:
        connection = mysql.connector.connect(
            host=DATABASE['host'],
            database=DATABASE['database'],
            user=DATABASE['user'],
            password=DATABASE['password']
        )
        cursor = connection.cursor()

        for platform, games in gameList.items():
            for game_id, game_info in games.items():
                name = game_id
                url = game_info['url']

                if platform == 'steam':
                    numeric_value = extract_numeric_value(url)
                    steamQuery(platform, cursor, name, url, connection, numeric_value, messageArray)
                else:
                    epicGogQuery(platform, cursor, name, url, connection, messageArray)



    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to extract platform names
def extract_platform(url, pattern):
    match = pattern.search(url)
    if match:
        platform = match.group(1)
        return platform_mapping.get(platform, platform)
    return None

# Function to add a game to the dictionary under a given key
def gameDict(my_dict, platform, game_id, url, name):
    if platform not in my_dict:
        my_dict[platform] = {}
    my_dict[platform][game_id] = {'url': url, 'name': name}


if __name__ == "__main__":
    #---------------------------------------------------------------------
    #Main
    #Log File config
    logging.basicConfig(filename='parser.log', encoding='utf-8', level=logging.DEBUG)

    # Define a mapping for known cases
    platform_mapping = {
        'steampowered': 'steam',
        'epicgames': 'epic',
        'gog': 'gog'
    }

    gameList = {}
    newGameList = []
    messageArray = []


    # Define a pattern to match the desired part of the URLs
    pattern = re.compile(r'(\b\w+)(?=\.com)')

    # Request the url
    url = "https://old.reddit.com/r/FreeGameFindings/"
    page = requests.get(url, headers = {'User-agent': 'your bot 0.1'})
    #print("Page Response : ", page)

    # parse html file and store into soup
    soup = BeautifulSoup(page.text, 'html.parser')
    toFile = soup.prettify()

    #string lists
    stores = ["store.steampowered.com","www.microsoft.com","store.epicgames.com","www.gog.com"]

    htmlResultList = parseData(soup, stores)

    #goes through and just pulls out the name of the game from the url/htmlResultList
    for urlItem in htmlResultList:
        tempString = urlItem.split("/")
        gameName = tempString.pop()
        if(gameName == ""):
            gameName = tempString.pop()

        gameName = gameName.replace("-", " ").replace("_", " ")
        
        # Extract platform names from the URLs
        storeName = extract_platform(urlItem, pattern)
        
        #stores information for database in gameList for use with messages later
        gameDict(gameList, storeName, gameName, urlItem, gameName)
        
  
    check_and_insert(gameList, messageArray)
  
    #should only contain new games that have not been entered into the database so we don't get duplicates
    message = """ """.join(messageArray)

    if message != '':
        logging.info(message)
        send_message(PHONENUMBER,'tmobile', message)
