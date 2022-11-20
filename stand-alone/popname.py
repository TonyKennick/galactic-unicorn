from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
import re
import time

gu = GalacticUnicorn()
width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT
MESSAGE_COLOUR = (255, 255, 255);
BACKGROUND_COLOUR = (0, 0, 0)
PADDING = 5

graphics = PicoGraphics(DISPLAY)
graphics.set_font("bitmap8")

string = "'\@ §ff0000§This is a §ff00ff§snail race"
message_for_length = ''

def hex_to_rgb (hexcolour):
    rgb = []
    hexregex = re.compile("([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])")
    hexmatch = re.match(hexregex,hexcolour)
    if hexmatch:
        r = int(hexmatch.group(1), 16)
        g = int(hexmatch.group(2), 16)
        b = int(hexmatch.group(3), 16)
        return (r, g, b)
    else:
        return MESSAGE_COLOUR

regex1 = re.compile("([^§]+)?")
regex2 = re.compile("§([0-9a-f]+)§([^§]+)")
match1 = re.match(regex1,string)
plain_message = False
texts = []
colours = []
lengths = []

if match1:

    pretext = match1.group(0)
    message_for_length = pretext 
    if len(pretext) == len(string):
        plain_message = True
        
if plain_message is False:
    if len(pretext):
        reduced_string = re.sub(r'.', '', string, match1.end(0))
        string = reduced_string
    
    while len(string) > 0:
        match2 = re.match(regex2,string)
        if match2:
            colour = match2.group(1)
            text = match2.group(2)
            message_for_length = message_for_length + text
            segment_length = graphics.measure_text(text, 1)
            texts.append(text)
            colours.append(colour)
            lengths.append(segment_length)
            reduced_string = re.sub(r'.', '', string, match2.end(0))
            string = reduced_string

HOLD_TIME = 2.0
STEP_TIME = 0.075

gu.set_brightness(0.5)
# state constants
STATE_PRE_SCROLL = 0
STATE_SCROLLING = 1
STATE_POST_SCROLL = 2

shift = 0
state = STATE_PRE_SCROLL

# calculate the message width so scrolling can happen
msg_width = graphics.measure_text(message_for_length, 1)
limit = msg_width + PADDING
last_time = time.ticks_ms()

while state != STATE_POST_SCROLL:
    time_ms = time.ticks_ms()

    if state == STATE_PRE_SCROLL and time_ms - last_time > HOLD_TIME * 1000:
        if msg_width + PADDING * 2 >= width:
            state = STATE_SCROLLING
        else:
            time.sleep(HOLD_TIME)
            state = STATE_POST_SCROLL
        last_time = time_ms

    if state == STATE_SCROLLING and time_ms - last_time > STEP_TIME * 1000:
        shift += 1
        if shift >= limit:
            state = STATE_POST_SCROLL
        last_time = time_ms

    graphics.set_pen(graphics.create_pen(int(BACKGROUND_COLOUR[0]), int(BACKGROUND_COLOUR[1]), int(BACKGROUND_COLOUR[2])))
    graphics.clear()
    
    if plain_message is True:
        graphics.set_pen(graphics.create_pen(int(MESSAGE_COLOUR[0]), int(MESSAGE_COLOUR[1]), int(MESSAGE_COLOUR[2])))
        graphics.text(string, PADDING - shift, 2, -1, 1)
        gu.update(graphics)
        
    else:
        
        if len(pretext):

            graphics.set_pen(graphics.create_pen(int(MESSAGE_COLOUR[0]), int(MESSAGE_COLOUR[1]), int(MESSAGE_COLOUR[2])))
            graphics.text(pretext, PADDING - shift, 2, -1, 1)
            gu.update(graphics)
            
        if len(colours):
            offset = graphics.measure_text(pretext, 1)
            for i in range(len(colours)):
                this_colour = hex_to_rgb(colours[i])

                graphics.set_pen(graphics.create_pen(int(this_colour[0]), int(this_colour[1]), int(this_colour[2])))
                graphics.text(texts[i], PADDING - shift + offset, 2, -1, 1)
                offset = offset + lengths[i]
                
            
    # update the display
    gu.update(graphics)

    # pause for a moment (important or the USB serial device will fail)
    time.sleep(0.001)


