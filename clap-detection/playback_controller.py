from pynput.keyboard import Key, Controller

keyboard = Controller()

keys = [Key.media_play_pause, Key.media_next, Key.media_previous]

def press_release(key: Key):
    keyboard.press(key)
    keyboard.release(key)


prompt = '''Enter a digit for action:
0 -> play/pause
1 -> next
2 -> previous
'''

if __name__ == "__main__":
    while True:
        val = int(input(prompt))
        if val == -1:
            break
        press_release(keys[val])

