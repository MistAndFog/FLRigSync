import re
from abc import ABC, abstractmethod


class CatClient(ABC):

    def __init__(self, ip, port):
        self.last_mode = "USB"
        self.last_freq = 0
        self._ip = ip
        self._port = port
        self._sock = None

    @abstractmethod
    def get_freq(self):
        pass

    @abstractmethod
    def get_mode(self):
        pass

    @abstractmethod
    def set_freq(self, freq):
        pass

    @abstractmethod
    def set_freq_mode(self, freq, mode=None):
        pass

    @abstractmethod
    def close():
        pass

    @abstractmethod
    def map_mode():
        pass

    def get_last_freq(self):
        return int(self.last_freq)

    def set_last_freq(self, freq):
        if freq and isinstance(freq, int):
            self._last_freq = freq

    def get_last_mode(self):
        return self.last_mode

    def set_last_mode(self, mode):
        if mode:
            self._last_mode = mode

    def _enter(self):
        self._last_freq = self.get_freq()
        self._last_mode = self.get_mode()


