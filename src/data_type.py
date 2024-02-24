#!/bin/python


class CoreInfo(object):
    def __init__(self, url: str, sid: str, flag='E'):
        self.url = url
        self.sid = sid
        self.flag = flag

    def __str__(self) -> str:
        return f'url: {self.url} sid: {self.sid} flag: {self.flag}'


class QueueInfo(object):
    def __init__(self, sid: str, date: str):
        self.sid = sid
        self.date = date

    def __str__(self) -> str:
        return f'sid: {self.sid} date: {self.date}'


class DUTConfig(object):
    def __init__(self, file: str, top: str, clk: str, commit: str):
        self.file = file
        self.top = top
        self.clk = clk
        self.commit = commit

    def __str__(self) -> str:
        return f'file: {self.file} clk: {self.clk} top: {self.top}'


class IverilogConfig(object):
    def __init__(self, commit: str):
        self.commit = commit

    def __str__(self) -> str:
        return f'commit: {self.commit}'


class VerilatorConfig(object):
    def __init__(self, commit: str):
        self.commit = commit

    def __str__(self) -> str:
        return f'commit: {self.commit}'


class VCSConfig(object):
    def __init__(self, freq: int, prog: str, wave: bool):
        self.freq = freq
        self.wave = wave
        self.prog = prog

    def __str__(self) -> str:
        return f'wave: {self.wave} prog: {self.prog} freq: {self.freq}'


class DCConfig(object):
    def __init__(self, freq: int, corner: str, retime: bool):
        self.freq = freq
        self.corner = corner
        self.retime = retime

    def __str__(self) -> str:
        return f'freq: {self.freq} corner: {self.corner} retime: {self.retime}'


class SubmitConfig(object):
    def __init__(self, dut_cfg: DUTConfig, iv_cfg: IverilogConfig,
                 ver_cfg: VerilatorConfig, vcs_cfg: VCSConfig,
                 dc_cfg: DCConfig):
        self.dut_cfg = dut_cfg
        self.iv_cfg = iv_cfg
        self.ver_cfg = ver_cfg
        self.vcs_cfg = vcs_cfg
        self.dc_cfg = dc_cfg

    def __str__(self) -> str:
        return f'''iv_cfg: {self.iv_cfg} ver_cfg: {self.ver_cfg}
                   vcs_cfg: {self.vcs_cfg} dc_cfg: {self.dc_cfg}'''
