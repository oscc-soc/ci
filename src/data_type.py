#!/bin/python

# Copyright (c) 2023 Beijing Institute of Open Source Chip
# ci is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#             http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

from typing import Tuple


class DUTInfo(object):
    def __init__(self, url: str, repo: str, flag='E'):
        self.url = url
        self.repo = repo
        self.flag = flag

    def __str__(self) -> str:
        return f'url: {self.url} repo: {self.repo} flag: {self.flag}'


class MetaConfig(object):
    def __init__(self, proj: str, auth: str, ver: str, notif: Tuple[str, str]):
        self.proj = proj
        self.auth = auth
        self.ver = ver
        self.notif = notif

    def __str__(self) -> str:
        return f'proj: {self.proj} auth: {self.auth} ver: {self.ver} notif: {self.notif}'


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
    def __init__(self, process: str, freq: int, corner: str, track: str,
                 volt_chnl: str, retime: bool, user: str):
        self.process = process
        self.freq = freq
        self.corner = corner
        self.track = track
        self.volt_chnl = volt_chnl
        self.retime = retime
        self.user = user

    def __str__(self) -> str:
        return f'''process: {self.process} freq: {str(self.freq)}
                   corner: {self.corner} track: {self.track}
                   volt_chnl: {self.volt_chnl} retime: {self.retime}
                   user: {self.user}'''


class CommitConfig(object):
    def __init__(self, repo: str, date: str, time: str):
        self.repo = repo
        self.date = date
        self.time = time

    def __str__(self) -> str:
        return f'repo: {self.repo} date: {self.date} time: {self.time}'


class SubmitConfig(object):
    def __init__(self, meta_cfg: MetaConfig, dut_cfg: DUTConfig,
                 iv_cfg: IverilogConfig, ver_cfg: VerilatorConfig,
                 vcs_cfg: VCSConfig, dc_cfg: DCConfig):
        self.meta_cfg = meta_cfg
        self.dut_cfg = dut_cfg
        self.iv_cfg = iv_cfg
        self.ver_cfg = ver_cfg
        self.vcs_cfg = vcs_cfg
        self.dc_cfg = dc_cfg

    def __str__(self) -> str:
        return f'''meta_cfg: {self.meta_cfg} dut_cfg: {self.dut_cfg}
                   iv_cfg: {self.iv_cfg} ver_cfg: {self.ver_cfg}
                   vcs_cfg: {self.vcs_cfg} dc_cfg: {self.dc_cfg}'''


class QueueInfo(object):
    def __init__(self, cmt_cfg: CommitConfig, sub_cfg: SubmitConfig):
        self.cmt_cfg = cmt_cfg
        self.sub_cfg = sub_cfg

    def __str__(self) -> str:
        return f'cmt_cfg: {self.cmt_cfg} sub_cfg: {self.sub_cfg}'
