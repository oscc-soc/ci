#!/bin/python

from enum import Enum
import os
import logging
import config
from data_type import DUTConfig, VCSConfig


class LogState(Enum):
    start = 0
    end = 1


class VCSTest(object):
    def __init__(self):
        self.date = ''
        self.time = ''
        self.lint = []
        self.warn = []
        self.err = []
        self.dut_cfg = DUTConfig('', '', '', '')
        self.vcs_cfg = VCSConfig(25, ('', ''), False)

    def clear(self):
        self.date = ''
        self.time = ''
        self.lint = []
        self.warn = []
        self.err = []
        self.dut_cfg = DUTConfig('', '', '', '')
        self.vcs_cfg = VCSConfig(25, ('', ''), False)
        self.clear_env()

    # clear test env
    def clear_env(self):
        os.chdir(config.VCS_RUN_DIR)
        cmd = 'make clean && rm temp.fp getReg* novas* verdi* -rf'
        os.system(cmd)
        os.chdir(config.VCS_CPU_DIR)
        cmd = 'find *.v | grep -v ysyx_210000.v | xargs rm -rf'
        os.system(cmd)
        os.chdir(config.HOME_DIR)

    def intg_soc(self):
        os.chdir(config.VCS_CPU_DIR)
        dut_path = config.SUB_DIR + '/' + self.dut_cfg.file
        os.system(f'cp -rf {dut_path} .')

        os.chdir(config.VCS_SCRIPT_DIR)
        os.system('python autowire.py')
        os.chdir(config.HOME_DIR)

    def comp(self):
        os.chdir(config.VCS_RUN_DIR)
        cmd = 'make comp'
        os.system(cmd)

        log_state = [LogState.end, LogState.end, LogState.end]
        # NOTE: receive comp log
        with open(config.VCS_RUN_DIR + '/compile.log', 'r',
                  encoding='utf-8') as fp:
            for line in fp:
                if line[0:4] == 'Lint':
                    log_state[0] = LogState.start
                elif line[0:7] == 'Warning':
                    log_state[1] = LogState.start
                elif line[0:5] == 'Error':
                    log_state[2] = LogState.start
                elif line == '\n':
                    log_state = [LogState.end, LogState.end, LogState.end]

                if log_state[0] == LogState.start:
                    self.lint.append(line)
                elif log_state[1] == LogState.start:
                    self.warn.append(line)
                elif log_state[2] == LogState.start:
                    self.err.append(line)

    def run(self):
        os.chdir(config.VCS_RUN_DIR)
        if self.vcs_cfg.prog[0] == '':
            os.system('make all-test')
        else:
            os.system(f'make {self.vcs_cfg.prog[0]}-{self.vcs_cfg.prog[1]}')

    def gen_rpt(self):
        rpt_path = config.RPT_DIR + '/' + self.dut
        rpt_path += f'/{self.date}-{self.time}'
        os.system(f'mkdir -p {rpt_path}')
        with open(rpt_path + '/vcs_report', 'a+', encoding='utf-8') as fp:
            fp.writelines(f'\ncore: {self.dut}\n')
            fp.writelines(
                '\n################\n#vcs compile log\n################\n')

            if not self.err or not self.warn or not self.lint:
                fp.writelines('all clear\n\n')
            else:
                fp.writelines(self.err + self.warn + self.lint)


vcstest = VCSTest()


def main(dut_cfg: DUTConfig, vcs_cfg: VCSConfig):
    logging.info(msg='[vcs test]')
    vcstest.clear()
    vcstest.dut_cfg = dut_cfg
    vcstest.vcs_cfg = vcs_cfg
    vcstest.intg_soc()
    vcstest.comp()
    vcstest.run()
    vcstest.gen_rpt()


if __name__ == '__main__':
    main(DUTConfig('', '', '', ''), VCSConfig(25, ('', ''), False))
