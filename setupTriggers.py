false = False
true = True

import json
import requests
import time
import re
from texttable import Texttable

#Spotipy is a python library that makes it very easy to work with the spotify API
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from secrets import Client_ID, Client_Secret #stored in secrets.py - this file is ignored by GIT

scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=Client_ID, client_secret=Client_Secret, redirect_uri='http://localhost'))

spotifyDevice = spotify.devices()
spotifyDeviceID = spotifyDevice['devices'][0]['id']

#load current song effects configuration
f = open('.\\songTriggers.json','r')
songTriggers = json.load(f)
f.close()

idList = []

for i in range(0, len(songTriggers)):
    idList.append(songTriggers[i]['id'])


def main():
    state = 0
    while(state == 0): #Ready to add a new trigger or view current ones



        userInput = input('Type a command and press enter. Type "help" for a list of commands\n')
        match userInput:
            case 'help':
                table = Texttable()
                table.header(["Command", "Description", "Parameters"])
                table.add_row(['add', 'adds a new trigger at the current timestamp in the current spotify song with the current light effects', 'none'])
                table.add_row(['listall', 'lists all the songs with current triggers', 'none'])
                table.add_row(['list <songIndex>', 'lists all the triggers of the provided song index', 'index of song in songTriggers. Find using command listall'])
                print(table.draw())
                
            case 'add':
                state = 1
            case 'listall':
                table = Texttable()
                table.header(['songIndex', 'songName', '# of triggers'])
                for i in range(0, len(songTriggers)):
                    table.add_row([i, songTriggers[i]['name'], len(list(songTriggers[i]['scenes']))])
                print(table.draw())

            


def saveEffectsToFile():
    f = open('.\\songTriggers.json','w')
    json.dump(songTriggers, f, indent=4)
    f.close()

def addScene(sceneName):
    payload = json.dumps({'name': sceneName})
    url = "http://127.0.0.1:8888/api/scenes"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.request('POST', url=url, headers=headers, data=payload)
        print(response)
    except Exception as e:
        print(e)

def changeScene(sceneName):
    url = "http://127.0.0.1:8888/api/scenes"
    payload = json.dumps({
        "id": sceneName,
        "action": "activate"
        })
    headers = {'Content-Type': 'application/json'}
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.text)

def deleteScene(sceneName):
    payload = json.dumps({'id': sceneName})
    url = "http://127.0.0.1:8888/api/scenes"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.request('DELETE', url=url, headers=headers, data=payload)
        responseObject = json.loads(response.text)
        responseFormatted = json.dumps(responseObject, indent = 2)
        print(responseFormatted)
    except Exception as e:
        print(e)

def setDeviceBlack(deviceID):
    payload = json.dumps(
        {
        "config": {
            "mirror": false,
            "color": "#000000",
            "background_color": "#000000",
            "blur": 0.0,
            "modulation_speed": 0.5,
            "modulation_effect": "sine",
            "flip": false,
            "speed": 1.0,
            "modulate": false,
            "brightness": 1.0,
            "background_brightness": 1.0
         },
        "name": "Single Color",
        "type": "singleColor"
        }
    )
    url = "http://127.0.0.1:8888/api/virtuals/"+deviceID+"/effects"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.request('POST', url=url, headers=headers, data=payload)
        responseObject = json.loads(response.text)
        responseFormatted = json.dumps(responseObject, indent = 2)
        print(responseFormatted)
    except Exception as e:
        print(e)

def addTrigger():
    try:
        currentPlayer = spotify.currently_playing()
        songID = currentPlayer['item']['id']
        songName = currentPlayer['item']['name']
        currentTimestamp = currentPlayer['progress_ms']
    except Exception as e:
        print(e)
        return

    sceneName = generateID(songName)+str(round(currentTimestamp/1000))
    
    inList = False
    songIndex = 0
    for i in range(0, len(idList)):
        if(songID == idList[i]):
            songIndex = i
            inList = True
            songTriggers[i]['scenes'][sceneName] = currentTimestamp
            saveEffectsToFile()
            break
        else:
            inList = False
    if(inList == False):
        data = {
        "id": songID,
        "name": songName,
        "scenes": {
            sceneName:currentTimestamp
            }
        }
        songTriggers.append(data)
        saveEffectsToFile()

    addScene(sceneName)
    return songIndex, sceneName

def generateID(name):
    #converts name into an ID that matches what LedFX will convert it to
    #taken straight from LedFX source code
    part1 = re.sub("[^a-zA-Z0-9]", " ", name).lower()
    return re.sub(" +", " ", part1).strip().replace(" ", "-")

def testTrigger(songIndex, sceneName):
    changeScene('alloff')
    try:
        spotify.pause_playback()
    except:
        pass
    
    if((songTriggers[songIndex]['scenes'][sceneName] - 2000) < 0):
        spotify.seek_track(0, spotifyDeviceID)
    else:
        spotify.seek_track(songTriggers[songIndex]['scenes'][sceneName] - 2000, spotifyDeviceID)
    
    spotify.start_playback()
    time.sleep(2)
    changeScene(sceneName)
    time.sleep(2)
    spotify.pause_playback()
    spotify.seek_track(songTriggers[songIndex]['scenes'][sceneName])


if __name__ == "__main__":
    main()





