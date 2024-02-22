import os
from typing import Any, Dict, Tuple
import tomli
import cicd_config
from data_type import IvConfig, VerConfig, VcsConfig, DcConfig


class Config(object):
    def __init__(self):
        self.commit_info = ''
        self.iv = IvConfig()
        self.ver = VerConfig()
        self.vcs = VcsConfig(False, 'all', 100)
        self.dc = DcConfig(100)

    def clear(self):
        pass

    def check_config(self, sid) -> Tuple[bool, str]:
        core_dir = cicd_config.SUB_DIR + '/' + sid
        core_config_file = core_dir + '/def_config.toml'
        # core_config_file = 'def_config.toml'
        if os.path.isfile(core_config_file):
            with open(core_config_file, 'rb') as fp:
                res = tomli.load(fp)
                print(res)

                cmd = f'git log origin/{cicd_config.BRANCH_NAME_DEV}'
                cmd += ' --pretty=format:"%s" -1'
                # print(cmd)
                os.chdir(core_dir)
                self.commit_info = cicd_config.exec_cmd(cmd)
                print(self.commit_info)
                os.chdir(cicd_config.HOME_DIR)
                # self.commit_info = 'vcs'
                # print(res.keys())
                std_config_keys = ['iv_config', 'ver_config', 'vcs_config']
                is_valid = False
                for v in std_config_keys:
                    if v in res.keys(
                    ) and res[v]['commit_info'] == self.commit_info:
                        print(f'[read {v}]')
                        is_valid = True
                        self.config_parse(res[v])
                return (is_valid, self.commit_info)
        else:
            return (False, '')

    def iv_config_parse(self, config: Dict[str, Any]):
        print(config)

    def ver_config_parse(self, config: Dict[str, Any]):
        print(config)

    def vcs_config_parse(self, config: Dict[str, Any]):
        # print(config)
        self.vcs.wave = config['wave'] == 'on'
        self.vcs.prog = config['prog']
        self.vcs.freq = config['freq']
        print(self.vcs)

    def dc_config_parse(self, config: Dict[str, Any]):
        print(config)
        self.dc.freq = config['freq']

    def config_parse(self, config: Dict[str, Any]):
        if self.commit_info == 'iv':
            self.iv_config_parse(config)
        elif self.commit_info == 'ver':
            self.ver_config_parse(config)
        elif self.commit_info == 'vcs':
            self.vcs_config_parse(config)
        elif self.commit_info == 'dc':
            self.dc_config_parse(config)


def_config = Config()


def main(sid: str) -> Tuple[bool, str]:
    res = def_config.check_config(sid)
    if res[0]:
        print(res)
    else:
        print('def_config.toml is not found or commit info is err!')
    return res


if __name__ == '__main__':
    main('')
