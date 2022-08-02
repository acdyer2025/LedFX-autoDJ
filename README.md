# General Overview

LedFX (see https://www.ledfx.app/) is a piece of software for led strip lighting. It allows for LED's to dance and react to the sound playing from your computer. For example, you could have your LED's flash perfectly in sync with the heavy bass of your favorite songs, among many other effects and options.

While this software is fantastic, it is missing a key feature that I think takes your music reactive lighting to the next level, which is the ability to change the effect based on a timestamp in a song. This project, LedFX-autoDJ, adds that capability for Spotify songs and is completely independent of the actual LedFX software.

For example, say your favorite song on Spotify has an intense ramp-up, and then subsequent base drop, at timestamp 1:15. This project allows you to easily setup LedFX to change the effect on the lights right at 1:15 when the base drops, bringing your lightshow to the next level. 

This project consists of two python programs:
* setupTriggers.py is the command-line utility to easily and quickly program in the effects and timestamps. It saves its routines and timestamps in songTriggers.json
* autoDJ.py should be running in the background during your lightshow. it reads from songTriggers.json and is responsible for detecting when a song that you have setup a special routine for is playing on Spotify. It then automatically talks to LedFX to coordinate the effects changing at the correct times in the song.

NOTE: This project is still in development, but the core functionality is done. Currently improving the user experience to make choreographing as easy and painless as possible, as well as refactoring to address bugs and edge cases. 

# Installation Instructions

TODO

# How to use

TODO (currently adding new commands and improving the choreographing workflow)