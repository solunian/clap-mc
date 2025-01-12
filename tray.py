import pystray
import time

from PIL import Image, ImageDraw


def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGBA', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.circle(
        (width // 2, height // 2),
        10,
        fill=color2)
    return image


# In order for the icon to be displayed, you must provide an icon
# icon = pystray.Icon(
#     'test name',
#     icon=create_image(32, 32, (1, 100, 1, 1), "white"))



global val, im

def callback():
    val = not val
    if val:
        icon = pystray.Icon("clap", icon=im)
    else:
        icon = pystray.Icon("nothing", icon=create_image(90))


def main():
    val = True
    im = open("clapping-hands-sign.png", "r")
    icon = pystray.Icon("clap", icon=im)

    # To finally show you icon, call run
    icon.run(setup=callback)

