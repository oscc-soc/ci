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
        self.def_vcs = VCSConfig(25, 'all', False)
        self.def_dc = DCConfig(100, 'TYP', False)
        self.sub_cfg = SubmitConfig(self.def_dut, self.def_iv, self.def_ver,
                                    self.def_vcs, self.def_dc)

    def clear(self):
        self.sub_cfg = SubmitConfig(self.def_dut, self.def_iv, self.def_ver,
                                    self.def_vcs, self.def_dc)

    def check_commit_info(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('commit_info') is None:
            return (False, 'dont have commit_info cfg')

        cmd = f'git log origin/{config.BRANCH_NAME_DEV}'
        cmd += ' --pretty=format:"%s" -1'
        logging.info(msg=cmd)
        self.commit_info = config.exec_cmd(cmd)
        logging.info(msg=self.commit_info)

        test_list = ['', 'vcs', 'dc']
        for v in test_list:
            if self.commit_info == v and cfg_list['commit_info'] == v:
                return (True, self.commit_info)
        return (False, 'dont have right commit info')

    def check_dut(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        # check and parse commit_info
        check_res = self.check_commit_info(cfg_list)
        if check_res[0] is False:
            return check_res

        return (False, 'dont have right dut info')

    def check_vcs(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        return (False, 'dont have right vcs cfg')

    def check_dc(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        return (False, 'dont have right dc cfg')

    def check(self, sid) -> Tuple[bool, str]:
        core_dir = config.SUB_DIR + '/' + sid
        core_cfg_file = core_dir + '/config.toml'
        # check if file is exist
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
                logging.info(msg=toml_cfg.keys())
                std_config_keys = ['iv_config', 'ver_config', 'vcs_config']
                is_valid = False
                for v in std_config_keys:
                    if v in toml_cfg.keys(
                    ) and toml_cfg[v]['commit_info'] == self.commit_info:
                        print(f'[read {v}]')
                        is_valid = True
                        self.config_parse(toml_cfg[v])
                return (is_valid, self.commit_info)
        else:
            return (False, 'config.toml dont exist')

    def parse_dut_config(self):
        pass

    def parse_iv_config(self, cfg: Dict[str, Any]):
        print(cfg)

    def parse_ver_config(self, cfg: Dict[str, Any]):
        print(cfg)

    def parse_vcs_config(self, cfg: Dict[str, Any]):
        # print(cfg)
        self.vcs.wave = cfg['wave'] == 'on'
        self.vcs.prog = cfg['prog']
        self.vcs.freq = cfg['freq']
        print(self.vcs)

    def parse_dc_config(self, cfg: Dict[str, Any]):
        print(cfg)
        self.dc.freq = cfg['freq']

    def parse(self, cfg: Dict[str, Any]):
        if self.commit_info == 'iv':
            self.parse_iv_config(cfg)
        elif self.commit_info == 'ver':
            self.parse_ver_config(cfg)
        elif self.commit_info == 'vcs':
            self.parse_vcs_config(cfg)
        elif self.commit_info == 'dc':
            self.parse_dc_config(cfg)


cfg_parser = ConfigParser()


def main(sid: str) -> Tuple[bool, str]:
    logging.info(msg='[parse dut cfg]')
    cfg_parser.clear()
    toml_cfg = cfg_parser.check(sid)
    if toml_cfg[0]:
        logging.info(msg=toml_cfg[1])
        cfg_parser.parse()
    else:
        logging.warning(msg='cfg.toml is not found or commit info is error!')
    return toml_cfg


if __name__ == '__main__':
    main('')
