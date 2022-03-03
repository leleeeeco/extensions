# --------------------

# List of id like : ["886735784", "284", "886738926", "886732682"]
# You can get the id from the furni data
FURNI_ID = [""]

# --------------------

# 2453 or something like that should work too
SPEECH_OUT = "Chat"
SPEECH_IN = "Chat"
UPDATE_FURNI = "ObjectUpdate"  # incoming furni update
ROOM_CHANGE = "RoomReady"  # incoming enter room

# --------------------

import sys
from g_python.gextension import Extension
from g_python.hmessage import Direction
from g_python.hpacket import HPacket

extension_info = {
    "title": "Count dice",
    "description": "Count the total for you",
    "version": "3.0",
    "author": "Lande"
}

ext = Extension(extension_info, sys.argv)
ext.start()

count = 0
around = []


def dice_moove(p):
    global count
    _, idd, x, y, _, _, _, _, _, state, _, _, _ = p.packet.read("iiiiissiisiii")
    idd = str(idd)
    state = int(state)

    if idd in FURNI_ID:
        if state > 0:
            if around:
                if (around[0]-1 <= x <= around[0]+1) and (around[1]-1 <= y <= around[1]+1):
                    count += state
                    talk(f" {str(state)} => {str(count)}")
            else:
                count += state
                talk(f" {str(state)} => {str(count)}")


def speech(p):
    global count, around
    text, _, _ = p.packet.read('sii')

    if text.lower().startswith(":creset"):
        p.is_blocked = True
        count = 0
        return talk("Count reset")

    if text.lower().startswith(":around reset"):
        p.is_blocked = True
        around = []
        return talk("Around reset")

    if text.lower().startswith(":around"):
        p.is_blocked = True
        text = text[8:]

        try:
            x, y = text.split(";")
        except ValueError:
            return talk("Format : `:around x;y`")
        try:
            x = int(x)
            y = int(y)
        except ValueError:
            return talk("Only number available")

        around = [x, y]
        talk(f"Around set to: {str(x)}x and {str(y)}y")


def talk(message):
    ext.send_to_client(HPacket(SPEECH_IN, 0, message, 0, 1, 0, 0))


def room_change(_):
    around.clear()


ext.intercept(Direction.TO_CLIENT, dice_moove, UPDATE_FURNI)
ext.intercept(Direction.TO_SERVER, speech, SPEECH_OUT)
ext.intercept(Direction.TO_CLIENT, room_change, ROOM_CHANGE)
