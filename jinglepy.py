import dbus
import subprocess
import time



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






iface.VolumeSet(90)
iface.VolumeGet()
