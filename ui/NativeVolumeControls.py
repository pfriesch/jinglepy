import platform
import subprocess
import time

system = platform.system()

if system == "Darwin":

    class NativeVolumeControls:

        def play(self):
            command = "osascript -e 'tell application \"Spotify\" to play'"
            result = subprocess.check_output(command, shell=True)

            return 0

        def stop(self):
            command = "osascript -e 'tell application \"Spotify\" to pause'"
            result = subprocess.check_output(command, shell=True)
            return 0

        def volume_get(self):
            command = f"osascript -e 'get output volume of (get volume settings)'"

            result = subprocess.check_output(command, shell=True)

            return int(result)

        def volume_set(self, cur_vol: int):
            cur_vol = min(max(0, int(cur_vol)), 100)
            command = f"osascript -e 'set volume output volume {cur_vol}'"

            result = subprocess.check_output(command, shell=True)

            return 0

# elif system == "Windows":
#
#     import win32api
#
#     from ctypes import cast, POINTER
#     from comtypes import CLSCTX_ALL
#     from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#
#
#     class NativeVolumeControls:
#         VK_MEDIA_PLAY_PAUSE = 0xB3
#         VK_MEDIA_STOP = 0xB2
#
#         def __init__(self):
#             self.devices = AudioUtilities.GetSpeakers()
#             self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#             self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
#
#         def play(self):
#             hwcode = win32api.MapVirtualKey(NativeVolumeControls.VK_MEDIA_PLAY_PAUSE, 0)
#             win32api.keybd_event(NativeVolumeControls.VK_MEDIA_PLAY_PAUSE, hwcode)
#             return 0
#
#         def stop(self):
#             hwcode = win32api.MapVirtualKey(NativeVolumeControls.VK_MEDIA_STOP, 0)
#             win32api.keybd_event(NativeVolumeControls.VK_MEDIA_STOP, hwcode)
#             return 0
#
#         def volume_get(self):
#             result = self.volume.GetMasterVolumeLevelScalar()
#             return int(result)
#
#         def volume_set(self, cur_vol: int):
#             cur_vol = min(max(0, int(cur_vol)), 100)
#             result = self.volume.SetMasterVolumeLevelScalar(cur_vol, None)
#             return 0

else:
    raise "Unsupported OS"
