
#This is a set of setup functions and utility functions that
#both autoDJ and setupTriggers use
#This file MUST be imported into both autoDJ and setupTriggers

import json
import requests
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from secrets import Client_ID, Client_Secret #stored in secrets.py - this file is ignored by GIT

scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=Client_ID, client_secret=Client_Secret, redirect_uri='https://www.google.com'))

spotifyDevice = spotify.devices()
spotifyDeviceID = spotifyDevice['devices'][0]['id']

#load song effects list
f = open('.\\songTriggers.json','r')
songTriggers = json.load(f)
f.close()

idList = []

for i in range(len(songTriggers)):
    idList.append(songTriggers[i]['id'])

def playSongScenes(songIndex, temporaryTime):
    currentSongSceneList = list(songTriggers[songIndex]['scenes'])
    currentSongSceneList.sort()
    currentSongTimestamps = []
    for i in range(len(currentSongSceneList)):
        currentSongTimestamps.append(songTriggers[songIndex]['scenes'][currentSongSceneList[i]])
    currentSongTimestamps.sort()
    
    currentScene = ''
    prevScene = ''
    prevID = ''
    onEndScene = False
    exitFlag = False
    prevTime = time.time()
    currentTime = 0

    while(exitFlag == False):
        try:
            currentPlayer = spotify.currently_playing()
        except Exception as e:
            print(e)
            exitFlag = True
            return exitFlag
        else:
            try:
                currentSongID = currentPlayer['item']['id']
                currentTimestamp = currentPlayer['progress_ms']
                prevID = currentSongID
            except TypeError:
                print('Spotify Unavailable')
                currentSongID = ''
                exitFlag = True
                return exitFlag
            except Exception as e:
                print(e)
            
            if(prevID != currentSongID):
                exitFlag = True
                return exitFlag
            
            for i in range(len(currentSongTimestamps)):
                if(currentTimestamp <= currentSongTimestamps[i]):
                    try:
                        currentScene = currentSongSceneList[i-1]
                        onEndScene = False
                        break
                    except IndexError:
                        currentScene = currentSongSceneList[0]
                        onEndScene = False
                        break
                else:
                    onEndScene = True
            
            if(onEndScene == True):
                currentScene = currentSongSceneList[-1] #grabs last scene in scene list

            if(prevScene != currentScene):
                changeScene(currentScene)
                prevScene = currentScene
        
        if(temporaryTime != 0):
            currentTime = time.time()
            if((currentTime - prevTime) > temporaryTime):
                exitFlag = True


def changeScene(sceneName):
    url = "http://127.0.0.1:8888/api/scenes"
    payload = json.dumps({
        "id": sceneName,
        "action": "activate"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.text)