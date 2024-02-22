#!/bin/python


class CoreInfo(object):
    def __init__(self, url: str, sid: str, flag='E'):
        self.url = url
        self.sid = sid
        self.flag = flag


class QueueInfo(object):
    def __init__(self, sid: str, date: str):
        self.sid = sid
        self.date = date


class IvConfig(object):
    def __init__(self):
        pass


class VerConfig(object):
    def __init__(self):
        pass


class VcsConfig(object):
    def __init__(self, wave: bool, prog: str, freq: int):
        self.wave = wave
        self.prog = prog
        self.freq = freq

    def __str__(self) -> str:
        return f'wave: {self.wave} prog: {self.prog} freq: {self.freq}'


class DcConfig(object):
    def __init__(self, freq: int):
        self.freq = freq
