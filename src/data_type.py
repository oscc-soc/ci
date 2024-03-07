#!/bin/python

from typing import Tuple


class DUTInfo(object):
    def __init__(self, url: str, repo: str, flag='E'):
        self.url = url
        self.repo = repo
        self.flag = flag

    def __str__(self) -> str:
        return f'url: {self.url} repo: {self.repo} flag: {self.flag}'


class DUTConfig(object):
    def __init__(self, arch: str, file: str, top: str, clk: str, commit: str):
        self.arch = arch
        self.file = file
        self.top = top
        self.clk = clk
        self.commit = commit

    def __str__(self) -> str:
        return f'arch: {self.arch} file: {self.file} clk: {self.clk} top: {self.top}'


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
    def __init__(self, freq: int, prog: Tuple[str, str], wave: bool):
        self.freq = freq
        self.prog = prog
        self.wave = wave

    def __str__(self) -> str:
        return f'freq: {self.freq} prog: {self.prog} wave: {self.wave}'


class DCConfig(object):
    def __init__(self, freq: int, corner: str, retime: bool):
        self.freq = freq
        self.corner = corner
        self.retime = retime

    def __str__(self) -> str:
        return f'freq: {self.freq} corner: {self.corner} retime: {self.retime}'


class CommitConfig(object):
    def __init__(self, repo: str, date: str, time: str):
        self.repo = repo
        self.date = date
        self.time = time

    def __str__(self) -> str:
        return f'repo: {self.repo} date: {self.date} time: {self.time}'


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
        return f'''dut_cfg: {self.dut_cfg} iv_cfg: {self.iv_cfg}
                   ver_cfg: {self.ver_cfg} vcs_cfg: {self.vcs_cfg} 
                   dc_cfg: {self.dc_cfg}'''


class QueueInfo(object):
    def __init__(self, cmt_cfg: CommitConfig, sub_cfg: SubmitConfig):
        self.cmt_cfg = cmt_cfg
        self.sub_cfg = sub_cfg

    def __str__(self) -> str:
        return f'cmt_cfg: {self.cmt_cfg} sub_cfg: {self.sub_cfg}'
