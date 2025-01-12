import pyaudio
import pynput
import playback_controller
import struct
import sys
import math

THRESHOLD_START = 0.1
CLAP_MAX_HIGH_SECONDS = 0.05
BACKGROUND_SECONDS = 10
CHUNK_SECONDS = 0.015

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
    print(block[10:12])
    BLOCK_SIZE = len(block) // 2

    highPassed = bytearray(len(block))
    rc = CHUNK_SECONDS / (len(block)/2)
    alpha = rc / (rc + CHUNK_SECONDS)

    highPassed[0] = block[0]
    highPassed[1] = block[1]

    for i in range(1, BLOCK_SIZE):
        index = i << 1
        print((struct.unpack('h', highPassed[index-2:index])[0], struct.unpack('h', block[index:index+2])[0], - struct.unpack('h', block[index-2:index])[0]))
        computed = alpha * (struct.unpack('h', highPassed[index-2:index])[0] + struct.unpack('h', block[index:index+2])[0] - struct.unpack('h', block[index-2:index])[0])
        print(computed)
        highPassed[index], highPassed[index+1] = struct.pack('h', computed)
    
    return highPassed

averageLow = 0
averageSize = 0
highChunks = 0

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

while not shouldQuit:
    block = stream.read(CHUNK)
    #block = highpass(block)
    rms = rootmeansquare(block)

    if THRESHOLD_START < rms and averageLow * 2 < rms:
        highChunks += 1
    else:
        if 1 <= highChunks <= CLAP_MAX_HIGH_CHUNKS:
            print("clap detected", rms, averageLow)
            playback_controller.press_release(playback_controller.keys[0])
        else:
            averageLow = (averageLow * averageSize + rms) / (averageSize + 1)
            averageSize = min(averageSize + 1, BACKGROUND_CHUNKS)
        highChunks = 0

listener.stop()
stream.close()
p.terminate()