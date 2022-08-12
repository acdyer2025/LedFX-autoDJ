import threading
import time
from autoDJutils import * #contains utility functions and setup code that is shared between
                          #autoDJ and setupTriggers

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
            newSong = playSongScenes(currentSongIndex, 0)
            if(newSong == True):
                state = 0
                currentSongID = ''      

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