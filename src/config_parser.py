import os
import logging
from typing import Any, Dict, Tuple
import tomli
import config
from data_type import DUTConfig, IverilogConfig
from data_type import VerilatorConfig, VCSConfig, DCConfig, SubmitConfig


class ConfigParser(object):
    def __init__(self):
        self.def_dut = DUTConfig('', '', '', '')
        self.def_iv = IverilogConfig('')
        self.def_ver = VerilatorConfig('')
        self.def_vcs = VCSConfig(25, ('', ''), False)
        self.def_dc = DCConfig(100, 'TYP', False)
        self.sub_cfg = SubmitConfig(self.def_dut, self.def_iv, self.def_ver,
                                    self.def_vcs, self.def_dc)

    def clear(self):
        self.sub_cfg = SubmitConfig(self.def_dut, self.def_iv, self.def_ver,
                                    self.def_vcs, self.def_dc)

    def check_file_top_clk(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('file') is None:
            return (False, 'dont have file cfg item')
        if cfg_list.get('top') is None:
            return (False, 'dont have top cfg item')
        if cfg_list.get('clk') is None:
            return (False, 'dont have clk cfg item')

        # check if dut file exists
        if os.path.isfile(cfg_list['file']):
            if config.find_str(
                    cfg_list['file'],
                    f'\\s*module\\s*{cfg_list["top"]}\\s*[\\(\\)|\\(|\\s*]'
            ) is False:
                return (False, 'top module dont exist')

            # not check if clk signal is in top module
            if config.find_str(
                    cfg_list['file'],
                    f'\\s*module\\s*{cfg_list["clk"]}\\s*,') is False:
                return (False, 'clk signal in top module dont exist')
        else:
            return (False, 'dut file dont exist')

        self.sub_cfg.dut_cfg.file = cfg_list['file']
        self.sub_cfg.dut_cfg.top = cfg_list['top']
        self.sub_cfg.dut_cfg.clk = cfg_list['clk']
        return (True, 'file, top and clk check done with no error')

    def check_freq(self, cfg_list: Dict[str, Any],
                   tab: str) -> Tuple[bool, str]:
        if cfg_list.get('freq') is None:
            return (False, 'dont have freq cfg item')

        freq = cfg_list['freq']
        if isinstance(freq, str):
            freq = int(freq)

        if tab == 'vcs':
            self.sub_cfg.vcs_cfg.freq = freq
            return (True, 'freq check done with no error')
        elif tab == 'dc':
            # check if freq is in range [100, 800, step=50]
            for val in range(100, 850, 50):
                if val == freq:
                    self.sub_cfg.dc_cfg.freq = freq
                    return (True, 'freq check done with no error')

        return (False, 'freq cfg item value is wrong')

    def check_prog(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('prog') is None:
            return (False, 'dont have prog cfg item')

        prog = cfg_list['prog']
        if prog.get('name') is None:
            return (False, 'dont have prog sub name cfg item')

        if prog.get('type') is None:
            return (False, 'dont have prog sub type cfg item')

        test_name_list = ['hello', 'memtest', 'rtthread']
        test_type_list = ['flash', 'mem', 'sdram']

        for vn in test_name_list:
            for vt in test_type_list:
                if (vn == prog['name'] and vt == prog['type']):
                    self.sub_cfg.vcs_cfg.prog = (prog['name'], prog['type'])
                    return (True, 'prog check done with no error')

        return (False, 'prog cfg item value is wrong')

    def check_wave(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('wave') is None:
            return (False, 'dont have wave cfg item')

        switch_list = ['off', 'on']
        for v in switch_list:
            if v == cfg_list['wave']:
                self.sub_cfg.vcs_cfg.wave = cfg_list['wave']
                return (True, 'wave check done with no error')

        return (False, 'wave item value is wrong')

    def check_corner(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('corner') is None:
            return (False, 'dont have corner cfg item')

        corner_list = ['WCZ', 'MAX', 'WCL', 'TYP', 'MIN', 'ML', 'MZ']
        for v in corner_list:
            if v == cfg_list['corner']:
                self.sub_cfg.dc_cfg.corner = cfg_list['corner']
                return (True, 'corner check done with no error')

        return (False, 'corner item value is wrong')

    def check_retime(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('retime') is None:
            return (False, 'dont have retime cfg item')

        switch_list = ['off', 'on']
        for v in switch_list:
            if v == cfg_list['retime']:
                self.sub_cfg.dc_cfg.retime = cfg_list['retime']
                return (True, 'retime check done with no error')

        return (False, 'retime item value is wrong')

    def check_commit(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('commit') is None:
            return (False, 'dont have commit cfg item')

        # exec git cmd to get commit info
        cmd = f'git log origin/{config.BRANCH_NAME_DEV}'
        cmd += ' --pretty=format:"%s" -1'
        logging.info(msg=cmd)
        self.sub_cfg.dut_cfg.commit = config.exec_cmd(cmd)
        logging.info(msg=self.sub_cfg.dut_cfg.commit)

        # check if git cmd is valid and equal to config toml value
        test_list = ['', 'vcs', 'dc']
        for v in test_list:
            if self.sub_cfg.dut_cfg.commit == v:
                return (True, 'commit check done with no error')
        return (False, 'commit cfg item value is wrong')

    def check_dut(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('dut') is None:
            return (False, 'dont have dut cfg table')

        check_res = self.check_file_top_clk(cfg_list['dut'])
        if check_res[0] is False:
            return check_res
        # check and parse commit_info
        check_res = self.check_commit(cfg_list['dut'])
        if check_res[0] is False:
            return check_res

        return (True, 'check dut cfg table done with no error')

    def check_vcs(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('vcs') is None:
            return (False, 'dont have vcs cfg table')

        check_res = self.check_freq(cfg_list['vcs'], 'vcs')
        if check_res[0] is False:
            return check_res

        check_res = self.check_prog(cfg_list['vcs'])
        if check_res[0] is False:
            return check_res

        check_res = self.check_wave(cfg_list['vcs'])
        if check_res[0] is False:
            return check_res

        return (True, 'check vcs cfg table done with no error')

    def check_dc(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('dc') is None:
            return (False, 'dont have dc cfg table')

        check_res = self.check_freq(cfg_list['dc'], 'dc')
        if check_res[0] is False:
            return check_res

        check_res = self.check_corner(cfg_list['dc'])
        if check_res[0] is False:
            return check_res

        check_res = self.check_retime(cfg_list['dc'])
        if check_res[0] is False:
            return check_res

        return (True, 'check dc cfg table done with no error')

    def check(self, sid) -> Tuple[bool, str]:
        core_dir = config.SUB_DIR + '/' + sid
        core_cfg_file = core_dir + '/config.toml'
        # check if config toml exists
        if os.path.isfile(core_cfg_file):
            with open(core_cfg_file, 'rb') as fp:
                toml_cfg = tomli.load(fp)
                logging.info(msg=toml_cfg)

                os.chdir(core_dir)
                # check and parse config
                check_res = self.check_dut(toml_cfg)
                if check_res[0] is False:
                    return check_res

                check_res = self.check_vcs(toml_cfg)
                if check_res[0] is False:
                    return check_res

                check_res = self.check_dc(toml_cfg)
                if check_res[0] is False:
                    return check_res

                os.chdir(config.HOME_DIR)
                return (True, 'parse config.toml with no error')
        else:
            return (False, 'config.toml dont exist')


cfg_parser = ConfigParser()


def main(sid: str) -> Tuple[bool, str]:
    logging.info(msg='[parse dut cfg]')
    cfg_parser.clear()
    toml_cfg = cfg_parser.check(sid)
    if toml_cfg[0]:
        logging.info(msg=toml_cfg[1])
    else:
        logging.warning(msg='config.toml is not found or has some errors')
    return toml_cfg


if __name__ == '__main__':
    main('')
