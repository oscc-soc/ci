import os
import copy
import logging
from typing import Any, Dict, Tuple, List
import tomli
import config
from data_type import DUTConfig, IverilogConfig
from data_type import VerilatorConfig, VCSConfig
from data_type import DCConfig, SubmitConfig


class ConfigParser(object):
    def __init__(self):
        self.def_dut = DUTConfig('', '', '', '', '')
        self.def_iv = IverilogConfig('')
        self.def_ver = VerilatorConfig('')
        self.def_vcs = VCSConfig(25, ('', ''), False)
        self.def_dc = DCConfig('', 100, 'TYP', '', '', False, '')
        self.sub_cfg = SubmitConfig(self.def_dut, self.def_iv, self.def_ver,
                                    self.def_vcs, self.def_dc)

    def clear(self):
        self.sub_cfg = SubmitConfig(self.def_dut, self.def_iv, self.def_ver,
                                    self.def_vcs, self.def_dc)

    def check_item(self, item: str, cfg_list: Dict[str, Any],
                   option_list: List[str]) -> Tuple[bool, str, str]:
        if cfg_list.get(item) is None:
            return (False, f'dont have {item} cfg item', '')

        item_val = cfg_list[item]
        for v in option_list:
            if v == item_val:
                return (True, f'{item} check done with no error', v)

        return (False, f'{item} cfg item value is wrong', '')

    def check_arch(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        option_list = ['rv32e', 'rv32i', 'rv32im', 'rv64i', 'rv64im']
        (ck_state, ck_info, ck_val) = self.check_item('arch', cfg_list,
                                                      option_list)
        if ck_state:
            self.sub_cfg.dut_cfg.arch = ck_val
        return (ck_state, ck_info)

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
            # if config.find_str(cfg_list['file'],
            #                    f'\\s*{cfg_list["clk"]}\\s*') is False:
            #     return (False, 'clk signal in top module dont exist')
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

        for vn in config.TESTCASE_NAME_LIST:
            for vt in config.TESTCASE_TYPE_LIST:
                if (vn == prog['name'] and vt == prog['type']):
                    self.sub_cfg.vcs_cfg.prog = (prog['name'], prog['type'])
                    return (True, 'prog check done with no error')

        if prog['name'] == '':
            self.sub_cfg.vcs_cfg.prog = ('all', 'all')
            return (True, 'prog check done with no error')

        return (False, 'prog cfg item value is wrong')

    def check_wave(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        option_list = ['off', 'on']
        (ck_state, ck_info, ck_val) = self.check_item('wave', cfg_list,
                                                      option_list)
        if ck_state:
            self.sub_cfg.vcs_cfg.wave = ck_val
        return (ck_state, ck_info)

    def check_process(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        option_list = ['28', '40', '110', '130']
        (ck_state, ck_info, ck_val) = self.check_item('process', cfg_list,
                                                      option_list)
        if ck_state:
            self.sub_cfg.dc_cfg.process = ck_val
        return (ck_state, ck_info)

    def check_corner(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        option_list = ['WCZ', 'MAX', 'WCL', 'TYP', 'MIN', 'ML', 'MZ']
        (ck_state, ck_info, ck_val) = self.check_item('corner', cfg_list,
                                                      option_list)
        if ck_state:
            self.sub_cfg.dc_cfg.corner = ck_val
        return (ck_state, ck_info)

    def check_track(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        option_list = ['8T', '9T', '10T', '11T', '12T']
        (ck_state, ck_info, ck_val) = self.check_item('track', cfg_list,
                                                      option_list)
        if ck_state:
            self.sub_cfg.dc_cfg.track = ck_val
        return (ck_state, ck_info)

    # dont use
    def check_volt_chnl(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        option_list = ['SVT40', 'LVT40']
        (ck_state, ck_info, ck_val) = self.check_item('volt_chnl', cfg_list,
                                                      option_list)
        if ck_state:
            self.sub_cfg.dc_cfg.volt_chnl = ck_val
        return (ck_state, ck_info)

    def check_retime(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        option_list = ['off', 'on']
        (ck_state, ck_info, ck_val) = self.check_item('retime', cfg_list,
                                                      option_list)
        if ck_state:
            self.sub_cfg.dc_cfg.retime = ck_val
        return (ck_state, ck_info)

    def check_commit(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        option_list = ['', 'vcs', 'dc']
        (ck_state, ck_info, ck_val) = self.check_item('commit', cfg_list,
                                                      option_list)
        if ck_state:
            self.sub_cfg.dut_cfg.commit = ck_val
        return (ck_state, ck_info)

    def check_dut(self, cfg_list: Dict[str, Any]) -> Tuple[bool, str]:
        if cfg_list.get('dut') is None:
            return (False, 'dont have dut cfg table')

        check_res = self.check_arch(cfg_list['dut'])
        if check_res[0] is False:
            return check_res

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

        check_res = self.check_process(cfg_list['dc'])
        if check_res[0] is False:
            return check_res

        check_res = self.check_freq(cfg_list['dc'], 'dc')
        if check_res[0] is False:
            return check_res

        check_res = self.check_corner(cfg_list['dc'])
        if check_res[0] is False:
            return check_res

        check_res = self.check_track(cfg_list['dc'])
        if check_res[0] is False:
            return check_res

        check_res = self.check_retime(cfg_list['dc'])
        if check_res[0] is False:
            return check_res

        return (True, 'check dc cfg table done with no error')

    def check(self, repo) -> Tuple[bool, str]:
        core_dir = f'{config.SUB_DIR}/{repo}'
        core_cfg_file = f'{core_dir}/config.toml'
        logging.info(msg=core_cfg_file)
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


def main(repo: str) -> Tuple[bool, str]:
    logging.info(msg='[parse dut cfg]')
    cfg_parser.clear()
    toml_cfg = cfg_parser.check(repo)
    if toml_cfg[0]:
        logging.info(msg=toml_cfg[1])
    else:
        logging.warning(msg=f'parse config.toml with errors: {toml_cfg[1]}')
    return toml_cfg


def submit_config() -> SubmitConfig:
    logging.info(msg=f'{cfg_parser.sub_cfg}')
    return copy.deepcopy(cfg_parser.sub_cfg)  # NOTE: copy class instance


if __name__ == '__main__':
    main('ysyx_000000')
