import pyaudio
import pynput
import numpy
import threading
import playback_controller
import struct
import sys
import math
import time

THRESHOLD_START = 0.015
CLAP_MAX_HIGH_SECONDS = 0.05
BACKGROUND_SECONDS = 10
CHUNK_SECONDS = 0.025

COMMAND_EXPIRATION_SECONDS = 1
COMMAND_RATIO_THRESHOLD = 1.5

def pressNTimes(k, n):
    for i in range(n):
        playback_controller.press_release(k)

COMMAND_LIST = {
    (2,0b0): (playback_controller.press_release, [pynput.keyboard.Key.media_play_pause]),
    (3,0b10): (playback_controller.press_release, [pynput.keyboard.Key.media_next]),
    (3,0b01): (playback_controller.press_release, [pynput.keyboard.Key.media_previous]),
    (4,0b100): (playback_controller.press_release, [pynput.keyboard.Key.media_volume_mute]),
    (4,0b101): (pressNTimes, [pynput.keyboard.Key.media_volume_down, 3]),
    (4,0b110): (pressNTimes, [pynput.keyboard.Key.media_volume_up, 3])
}

RATE = 44100

FORMAT = pyaudio.paInt16
CHANNELS = 1 if sys.platform == 'darwin' else 2

CHUNK = int(RATE * CHUNK_SECONDS)
BACKGROUND_CHUNKS = int(BACKGROUND_SECONDS / CHUNK_SECONDS)
CLAP_MAX_HIGH_CHUNKS = int(CLAP_MAX_HIGH_SECONDS / CHUNK_SECONDS)

shouldQuit = False

def onPress(key):
    global shouldQuit
    if key == pynput.keyboard.Key.esc:
        shouldQuit = True

listener = pynput.keyboard.Listener(on_press=onPress)
listener.start()

def rootmeansquare(block):
    BLOCK_SIZE = len(block) // 2
    s = 0.0
    for i in range(BLOCK_SIZE):
        iNorm = struct.unpack('h', block[i<<1 : (i<<1) + 2])[0] / 32768.0
        s += iNorm * iNorm
    
    return math.sqrt(s / BLOCK_SIZE)

def highpass(block):
    BLOCK_SIZE = len(block) // 2

    highPassed = bytearray(len(block))
    # rc = CHUNK_SECONDS / (len(block)/2)
    # alpha = rc / (rc + CHUNK_SECONDS)
    # print(alpha)
    highPassed[0] = block[0]
    highPassed[1] = block[1]

    for i in range(1, BLOCK_SIZE):
        index = i << 1
        #print((struct.unpack('h', highPassed[index-2:index])[0], struct.unpack('h', block[index:index+2])[0], - struct.unpack('h', block[index-2:index])[0]))
        #computed = (struct.unpack('h', highPassed[index-2:index])[0] + struct.unpack('h', block[index:index+2])[0] - struct.unpack('h', block[index-2:index])[0])
        computed = struct.unpack('h', block[index:index+2])[0] - struct.unpack('h', block[index-2:index])[0]
        highPassed[index], highPassed[index+1] = struct.pack('h', min(32767, max(computed, -32767)))
    
    return highPassed

chunkBuffer = [0]*BACKGROUND_CHUNKS
chunkIndex = -BACKGROUND_CHUNKS
averageLow = 0

highChunks = 0

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

commandClaps = []
runningThread = None

def expiry():
    global runningThread

    if len(commandClaps) == 0:
        return

    minDistance = -1
    ratios = []
    for i in range(len(commandClaps)-1):
        ratio = commandClaps[i+1]-commandClaps[i]
        ratios.append(ratio)
        if minDistance == -1 or minDistance > ratio:
            minDistance = ratio
    
    ratioFlags = 0
    for i in range(len(ratios)):
        if ratios[i] / minDistance > COMMAND_RATIO_THRESHOLD:
            ratioFlags += 1 << (len(ratios) - i - 1)
    
    print(("{:0%db}" % len(ratios)).format(ratioFlags))
    key = (1+len(ratios), ratioFlags)

    if key not in COMMAND_LIST:
        print(("no command mapped to {:%db}." % len(ratios)).format(ratioFlags))
    else:
        cmd = COMMAND_LIST[key]
        #print(cmd[0], cmd[1])
        cmd[0](*cmd[1])
        
    commandClaps.clear()
    runningThread = None

def onClap(t):
    global commandClaps
    global runningThread

    commandClaps.append(t)

    if runningThread != None:
        runningThread.cancel()
    
    runningThread = threading.Timer(COMMAND_EXPIRATION_SECONDS, expiry)
    runningThread.start()

while not shouldQuit:
    block = stream.read(CHUNK)
    block = highpass(block)
    rms = rootmeansquare(block)

    #print(rms)

    if THRESHOLD_START < rms and not averageLow * 2 < rms:
        print(averageLow * 2, rms)
        print("average low prevented")
    if THRESHOLD_START < rms and averageLow * 2 < rms:
        highChunks += 1
    else:
        if 1 <= highChunks <= CLAP_MAX_HIGH_CHUNKS:
            print("clap detected")
            onClap(time.time())
        else:
            chunkIndex = min(chunkIndex + 1, BACKGROUND_CHUNKS)
            if chunkIndex < 0:
                averageSize = chunkIndex + BACKGROUND_CHUNKS - 1
                averageLow = (averageLow * averageSize + rms) / (averageSize + 1)
            else:
                chunkIndex %= BACKGROUND_CHUNKS
                averageLow += (rms - chunkBuffer[chunkIndex]) / BACKGROUND_CHUNKS
                chunkBuffer[chunkIndex] = rms
        highChunks = 0
    
    #shouldQuit = True

listener.stop()
stream.close()
p.terminate()