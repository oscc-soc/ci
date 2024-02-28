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
        self.run_res = {}
        self.dut_cfg = DUTConfig('', '', '', '')
        self.vcs_cfg = VCSConfig(25, ('', ''), False)

    def clear(self):
        self.date = ''
        self.time = ''
        self.lint = []
        self.warn = []
        self.err = []
        self.run_res = {}
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

    def program(self, prog_name: str, prog_type: str):
        if prog_type == 'flash':
            os.system(
                f'ln -sf program/{prog_name}.{prog_type} mem_Q128_bottom.vmf')
        else:
            os.system(f'ln -sf program/jump.{prog_type} mem_Q128_bottom.vmf')
            os.system(
                f'ln -sf program/{prog_name}.{prog_type} init_{prog_type}.bin.txt'
            )

    def collect_comp_log(self):
        log_state = [LogState.end, LogState.end, LogState.end]
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

    def collect_run_log(self, prog_name: str, prog_type: str):
        with open(config.VCS_RUN_DIR + '/run.log', 'r',
                  encoding='utf-8') as fp:
            tmp_res = ''
            for line in fp:
                if not '/home' in line:
                    tmp_res += line
                if config.TESTCASE_RES_DICT[prog_name] in line:  # test pass
                    self.run_res[f'{prog_name}-{prog_type}'] = ''
                    return

            self.run_res[f'{prog_name}-{prog_type}'] = tmp_res

    def comp(self):
        os.chdir(config.VCS_RUN_DIR)
        os.system('make comp')
        self.collect_comp_log()

    def run(self):
        os.chdir(config.VCS_RUN_DIR)
        if self.vcs_cfg.prog[0] == '':
            for pl in config.TESTCASE_NAME_LIST:
                for mt in config.TESTCASE_TYPE_LIST:
                    self.program(pl, mt)
                    os.system(f'make run test={pl}-{mt}')
                    self.collect_run_log(pl, mt)

        else:
            self.program(self.vcs_cfg.prog[0], self.vcs_cfg.prog[1])
            os.system(
                f'make run test={self.vcs_cfg.prog[0]}-{self.vcs_cfg.prog[1]}')
            self.collect_run_log(self.vcs_cfg.prog[0], self.vcs_cfg.prog[1])

    def gen_rpt_dir(self) -> str:
        rpt_path = config.RPT_DIR + '/' + self.dut_cfg.top
        rpt_path += f'/{self.date}-{self.time}'
        os.system(f'mkdir -p {rpt_path}')
        return rpt_path

    def gen_comp_rpt(self) -> bool:
        rpt_path = self.gen_rpt_dir()
        with open(f'{rpt_path}/vcs_report', 'a+', encoding='utf-8') as fp:
            fp.writelines(f'\ndut: {self.dut_cfg.top}\n')
            fp.writelines(
                '\n################\n#vcs compile log\n################\n')

            if not self.err or not self.warn or not self.lint:
                fp.writelines('all clear\n\n')
                return True
            else:
                fp.writelines(self.err + self.warn + self.lint)
                return False

    def gen_run_res(self, prog_name: str, prog_type: str) -> str:
        res = ''

        if self.run_res[f'{prog_name}-{prog_type}'] == '':
            res += f'{prog_name} test in {prog_type} pass!!\n'
        else:
            res += f'{prog_name} test in {prog_type} fail!!\n'
            res += '======================================================\n'
            res += self.run_res[f'{prog_name}-{prog_type}']
            res += '======================================================\n\n'

        return res

    def gen_run_rpt(self) -> bool:
        rpt_path = self.gen_rpt_dir()
        with open(f'{rpt_path}/vcs_report', 'a+', encoding='utf-8') as fp:
            fp.writelines(
                '\n#####################\n#vcs program test\n#####################\n'
            )

            if self.vcs_cfg.prog[0] == '':
                for pl in config.TESTCASE_NAME_LIST:
                    for mt in config.TESTCASE_TYPE_LIST:
                        fp.writelines(self.gen_run_res(pl, mt))
            else:
                fp.writelines(
                    self.gen_run_res(self.vcs_cfg.prog[0],
                                     self.vcs_cfg.prog[1]))

        return True


vcstest = VCSTest()


def main(dut_cfg: DUTConfig, vcs_cfg: VCSConfig) -> bool:
    logging.info(msg='[vcs test]')
    vcstest.clear()
    vcstest.dut_cfg = dut_cfg
    vcstest.vcs_cfg = vcs_cfg
    vcstest.intg_soc()
    comp_res = True
    vcstest.comp()
    comp_res = vcstest.gen_comp_rpt()

    if comp_res is True:
        vcstest.run()
        run_info = vcstest.gen_run_rpt()
        return run_info

    return comp_res


if __name__ == '__main__':
    main(DUTConfig('', '', '', ''), VCSConfig(25, ('', ''), False))
