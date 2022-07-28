import json
import requests
import time
from threading import Timer

#Spotipy is a python library that makes it very easy to work with the spotify API
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from secrets import Client_ID, Client_Secret #stored in secrets.py - this file is ignored by GIT

scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=Client_ID, client_secret=Client_Secret, redirect_uri='http://localhost'))

#load song effects list
f = open('.\\songTriggers.json','r')
songTriggers = json.load(f)
f.close()

#songStatus = ['state', index_in_songTriggers.json, duration_ms, progress_ms, is_paused]
songStatus = ['',0,0,0,False]
idList = []

for i in range(0, len(songTriggers)):
    idList.append(songTriggers[i]['id'])
print(idList)

def main():

    #start timer to poll spotify every 3 seconds to get current song
    t = Timer(3, checkForSong, [idList, True])
    t.start()

    while(True):
        global songStatus
    
        if(songStatus[0] == 'inList'): #the song spotify is currently playing is one that effects exist for
            print('found song in list')
            currentSong = songStatus[1] #this gives us the index of where the scenes for this song are in soundEffects.json
            currentSongDuration = songStatus[2]
            currentSongTimestamp = songStatus[3]
            currentSongSceneList = list(songTriggers[currentSong]['scenes'])
            timeStamps = [] 
            for i in range(0, len(currentSongSceneList)):
                timeStamps.append(songTriggers[currentSong]['scenes'][currentSongSceneList[i]])
            
            #The following is a very hacky method to get the effects to trigger exactly on the right 
            #  timestamp of the song, as polling spotify constatntly to get the playback position would
            #  quickly rate limit us by spotify, which nobody wants
            #  There are better ways to do this, but this was quick to implement and works surprising well
            #Essentially, we figure out exactly where we are in the song and then use the basic time.time
            #  module to keep track of the playback without having to poll spotify
            #pausing the song breaks this because the effects will still be sent since we are not
            #  reyling on spotify anymore for the timestamp
            
            hasPlayed = list(timeStamps)
            prevTime = time.time()*1000
            prevSong = songStatus[1]

            while((time.time()*1000 - prevTime) <= (currentSongDuration - currentSongTimestamp)):
                #print("Running custom song effects")
                if(songStatus[1] != prevSong):
                    print("song changed")
                    break
                for i in range(0, len(timeStamps)):
                    if(time.time()*1000 - prevTime + currentSongTimestamp > timeStamps[i]):
                        if(hasPlayed[i] != True):
                            changeScene(currentSongSceneList[i])
                            hasPlayed[i] = True
            
            print("finished with current song")
            time.sleep(1)
            checkForSong(idList, False)

        elif(songStatus[0] == 'none'):
            print('found song not present in list')
            changeScene('default')
            currentSongDuration = songStatus[2]
            currentSongTimestamp = songStatus[3]
            prevTime = time.time()*1000
            prevSong = songStatus[1]

            #wait in this loop until the exact end of the song, then check for next one.
            #This allows us to theoreically get the effect to change right when the next song starts,
            #as opposed to somewhere in the 3 second window that the spotify polling is occuring
            while((time.time()*1000 - prevTime) <= (currentSongDuration - currentSongTimestamp)):
                if(songStatus[1] != prevSong):
                    print("song changed")
                    break

            print("finished with current song")
            time.sleep(1)
            checkForSong(idList, False)

        elif(songStatus[0] == 'spotifyUnavailable'):
            print("Spotify Client Unavaiable")
        else:
            pass

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

def checkForSong(idlist, startTimer):
    
    global songStatus
    print("checking for song")

    #
    if(startTimer == True):
        t = Timer(3, checkForSong, [idlist, True])
        t.start()

    try:
        currentPlayer = spotify.currently_playing()
        songID = currentPlayer['item']['id']
        songStatus[2] = currentPlayer['item']['duration_ms']
        songStatus[3] = currentPlayer['progress_ms']
        print(songStatus)
    except Exception as e:
        print(e)
        songStatus = ['spotifyUnavailable', -1, -1, -1]
        return

    for songIndex in range(0, len(idlist)):
        if(songID == idlist[songIndex]):
            songStatus[0] = 'inList'
            songStatus[1] = songIndex
            return 
        else:
            pass
    songStatus[0] = 'none'
    songStatus[1] = -1
    return

if __name__ == "__main__":
    main()