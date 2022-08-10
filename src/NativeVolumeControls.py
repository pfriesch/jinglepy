import platform

system = platform.system()

if system == "Darwin":
    import osascript


    class NativeVolumeControls:

        @classmethod
        def play(cls):
            result = osascript.osascript("tell application \"Spotify\" to play")
            return 0

        @classmethod
        def stop(cls):
            result = osascript.osascript("tell application \"Spotify\" to pause")
            return 0

        @classmethod
        def volume_get(cls):
            result = osascript.osascript(f"get output volume of (get volume settings)")

            return int(result[1])

        @classmethod
        def volume_set(cls, cur_vol: int):
            cur_vol = min(max(0, int(cur_vol)), 100)
            result = osascript.osascript(f"set volume output volume {cur_vol}")
            return 0

elif system == "Windows":

    import win32api

    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


    class NativeVolumeControls:
        VK_MEDIA_PLAY_PAUSE = 0xB3
        VK_MEDIA_STOP = 0xB2

        def __init__(self):
            self.devices = AudioUtilities.GetSpeakers()
            self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

        def play(self):
            hwcode = win32api.MapVirtualKey(NativeVolumeControls.VK_MEDIA_PLAY_PAUSE, 0)
            win32api.keybd_event(NativeVolumeControls.VK_MEDIA_PLAY_PAUSE, hwcode)
            return 0

        def stop(self):
            hwcode = win32api.MapVirtualKey(NativeVolumeControls.VK_MEDIA_STOP, 0)
            win32api.keybd_event(NativeVolumeControls.VK_MEDIA_STOP, hwcode)
            return 0

        def volume_get(self):
            result = self.volume.GetMasterVolumeLevelScalar()
            return int(result)

        def volume_set(self, cur_vol: int):
            cur_vol = min(max(0, int(cur_vol)), 100)
            result = self.volume.SetMasterVolumeLevelScalar(cur_vol, None)
            return 0

else:
    raise "Unsupported OS"
