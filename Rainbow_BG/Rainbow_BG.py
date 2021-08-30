import sys
from g_python.gextension import Extension
from g_python.hmessage import Direction
from time import sleep
import threading


extension_info = {
    "title": "Rainbow Background",
    "description": "Its cool",
    "version": "2.0",
    "author": "Lande"
}

ext = Extension(extension_info, sys.argv, silent=True)
ext.start()

""""""

SPEECH = "Chat"
MODIFY_FURNI = "SetRoomBackgroundColorData"
CLEAR_ID = "OpenFlatConnection"

SET_DELAY = "/r "
START = "/r on"
STOP = "/r off"
SET_ID = "/r set"

""""""

cool_down = 0.2
idd = ""
set_id = on = False


def speech(p):
    text, _, _ = p.packet.read('sii')
    global cool_down, on, set_id

    if text == SET_ID:
        p.is_blocked = True
        ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Modify the background to save the id"}{i:0}{i:30}{i:0}{i:0}')
        set_id = True

    elif text == START:
        p.is_blocked = True
        if on:
            return ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Already on"}{i:0}{i:30}{i:0}{i:0}')
        if idd:
            on = True
            thread = threading.Thread(target=main)
            thread.start()
            ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Rainbow on"}{i:0}{i:30}{i:0}{i:0}')
        else:
            ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Id not found"}{i:0}{i:30}{i:0}{i:0}')
            ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Please use `'+SET_ID+'`"}{i:0}{i:30}{i:0}{i:0}')

    elif text == STOP:
        p.is_blocked = True
        if not on:
            return ext.send_to_client('{in:'+SPEECH+'}{i:0}{s:"Already off"}{i:0}{i:30}{i:0}{i:0}')
        on = False
        ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Rainbow off"}{i:0}{i:30}{i:0}{i:0}')

    elif text.startswith(SET_DELAY):
        p.is_blocked = True
        try:
            delay = float(text[(len(SET_DELAY)):])
            cool_down = delay
            ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Interval set to: '+str(cool_down)+'"}{i:0}{i:30}{i:0}{i:0}')
        except ValueError:
            ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Only number available"}{i:0}{i:30}{i:0}{i:0}')


def main():
    while on:
        for i in range(256):
            if on:
                ext.send_to_server('{out:'+str(MODIFY_FURNI)+'}{i:'+str(idd)+'}{i:'+str(i)+'}{i:128}{i:128}')
                sleep(cool_down)


def save_id(p):
    global idd, set_id

    if set_id:
        furni_id, _, _, _ = p.packet.read("iiii")
        idd = str(furni_id)
        ext.send_to_client('{in:'+SPEECH+'}{i:123456789}{s:"Id save ('+idd+')"}{i:0}{i:30}{i:0}{i:0}')
        set_id = False


def clear(p):
    global idd, on
    on = False
    idd = ""


ext.intercept(Direction.TO_SERVER, speech, SPEECH)
ext.intercept(Direction.TO_SERVER, save_id, MODIFY_FURNI)
ext.intercept(Direction.TO_SERVER, clear, CLEAR_ID)
