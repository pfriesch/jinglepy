import dbus
import subprocess
import time
from curses import wrapper

#init Dbus interface
session_bus = dbus.SessionBus()

try:
    player = session_bus.get_object('org.mpris.clementine','/Player')
except:
    #launch clementine if needed
    clem = subprocess.Popen('clementine')
    time.sleep(2)
    player = session_bus.get_object('org.mpris.clementine','/Player')

iface = dbus.Interface(player,dbus_interface='org.freedesktop.MediaPlayer')

def main(stdscr):
    stdscr.clear()
    while True :
        stdscr.refresh()
        k=stdscr.getkey()
        
        options = { "p" : iface.Play ,
                    "s" : iface.Stop
                }
        try:
            options[k]()
        except:
            print("no function assigned")

        time.sleep(1)

#init curses
wrapper(main)

iface.VolumeSet(90)
iface.VolumeGet()
