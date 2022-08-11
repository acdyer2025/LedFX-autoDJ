import json
import requests
import threading
import time

#Spotipy is a python library that makes it very easy to work with the spotify API
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from secrets import Client_ID, Client_Secret #stored in secrets.py - this file is ignored by GIT

scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=Client_ID, client_secret=Client_Secret, redirect_uri='https://www.google.com'))

#load song effects list
f = open('.\\songTriggers.json','r')
songTriggers = json.load(f)
f.close()

idList = []

for i in range(len(songTriggers)):
    idList.append(songTriggers[i]['id'])

currentSongID = ''

def main():

    #start timer to poll spotify every 2 seconds to get current song
    checkForSongDelayTime = 2
    t = threading.Thread(target=checkForSong, args=(checkForSongDelayTime,), daemon=True)
    t.start()

    global currentSongID
    state = 0

    while(True):
        if(state == 0):
            changeScene('default')
            while(state == 0): #checking to see if the current spotify song ID is one that special effects exist for
                for i in range(len(idList)):
                    if(currentSongID == idList[i]): #current song is one that special effects exist for
                        state = 1
                        currentSongIndex = i
                        break
                    else:
                        state = 0
        
        while(state == 1):
            newSong = playSongScenes(currentSongIndex)
            if(newSong == True):
                state = 0
                currentSongID = ''      

def playSongScenes(songIndex):
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

def checkForSong(checkForSongDelayTime):
    while(True):
        global currentSongID
        try:
            currentPlayer = spotify.currently_playing()
        except Exception as e:
            print(e)
        else:
            try:
                currentSongID = currentPlayer['item']['id']
            except TypeError:
                print('Spotify Unavailable')
            except Exception as e:
                print(e)
        time.sleep(checkForSongDelayTime)
    

if __name__ == "__main__":
    main()