import osascript


class NativeVolumeControls:

    @classmethod
    def play(self):
        result = osascript.osascript("tell application \"Spotify\" to play")
        return 0

    @classmethod
    def stop(self):
        result = osascript.osascript("tell application \"Spotify\" to pause")
        return 0

    @classmethod
    def volume_get(cls):
        result = osascript.osascript(f"get output volume of (get volume settings)")

        return int(result[1])

    @classmethod
    def volume_set(cls, cur_vol: int):
        cur_vol = min(max(0, cur_vol), 100)
        osascript.osascript(f"set volume output volume {cur_vol}")
