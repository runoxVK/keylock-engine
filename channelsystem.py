import pygame as pg
import numpy as np


channels_list = ["Sound"]
channel_amount = len(channels_list)


def getChannel(name):
    return (channels_list.index(name))

def world(channels=channel_amount,x=12,y=12):
    state = np.zeros((channels,x,y), dtype=float)
    return state

    
def emit (state,x,y,channelName,mag):

    new_state = state.copy()

    if channelName == "Sound":
        print("Sound Channel!")
        new_state[getChannel("Sound"),x,y] += mag

    return new_state


def soundChannelUpdate(state):
    new_state = state.copy()
    soundChannel = new_state[getChannel("Sound")]
    shared = np.zeros_like(soundChannel)

    x,y = soundChannel.shape

    for i in range (0, x, 1):
        for j in range (0, y, 1):
            if shared[i,j] == 0:

                if soundChannel[i,j] > 0:
                    if soundChannel[i,j] <= 0.0625:
                        soundChannel[i,j] = 0

                    else:

                        if i+1 < x:
                            soundChannel[i+1,j] += (soundChannel[i,j] * (1/2))
                            shared[i+1,j] = 1
                        if i-1 >= 0:
                            soundChannel[i-1,j] += (soundChannel[i,j] * (1/2))
                            shared[i-1,j] = 1
                        
                        if j+1 < y:
                            soundChannel[i,j+1] += (soundChannel[i,j] * (1/2))
                            shared[i,j+1] = 1

                        if j-1 >= 0:
                            soundChannel[i,j-1] += (soundChannel[i,j] * (1/2))
                            shared[i,j-1] = 1

                        soundChannel[i,j] = 0

    return new_state

    


myState = world()
updated_state = emit(myState,6,6,"Sound",1)
print(updated_state[getChannel("Sound")])

ticked = soundChannelUpdate(updated_state)
print(ticked[getChannel("Sound")])

ticked = soundChannelUpdate(ticked)

print(ticked[getChannel("Sound")])





