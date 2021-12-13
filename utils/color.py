
import random


red =  (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)

colors = []
colors.append(red)
colors.append(green)
colors.append(blue)
colors.append(yellow)

def get_random_color():
    return colors[random.randrange(0, len(colors))]