#!/bin/python

from enum import Enum
import os
import logging
import config
from data_type import CommitConfig, DUTConfig, VCSConfig


class LogState(Enum):
    start = 0
    end = 1


class VCSTest(object):
    def __init__(self):
        self.lint = []
        self.warn = []
        self.err = []
        self.run_res = {}
        self.cmt_cfg = CommitConfig('', '', '')
        self.dut_cfg = DUTConfig('', '', '', '', '')
        self.vcs_cfg = VCSConfig(25, ('', ''), False)

    def clear(self):
        self.lint = []
        self.warn = []
        self.err = []
        self.run_res = {}
        self.cmt_cfg = CommitConfig('', '', '')
        self.dut_cfg = DUTConfig('', '', '', '', '')
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
        dut_path = f'{config.SUB_DIR}/{self.cmt_cfg.repo}/{self.dut_cfg.file}'
        os.system(f'cp -rf {dut_path} .')

        os.chdir(config.VCS_SCRIPT_DIR)
        os.system('python autowire.py')
        os.chdir(config.HOME_DIR)

    def program(self, arch: str, prog_name: str, prog_type: str):
        if prog_type == 'flash':
            os.system(
                f'ln -sf program/{arch}/{prog_name}.{prog_type} mem_Q128_bottom.vmf'
            )
        else:
            os.system(
                f'ln -sf program/{arch}/jump.{prog_type} mem_Q128_bottom.vmf')
            os.system(
                f'ln -sf program/{arch}/{prog_name}.{prog_type} init_{prog_type}.bin.txt'
            )

    def collect_comp_log(self):
        log_state = [LogState.end, LogState.end, LogState.end]
        with open(f'{config.VCS_RUN_DIR}/compile.log', 'r',
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
        with open(f'{config.VCS_RUN_DIR}/run.log', 'r',
                  encoding='utf-8') as fp:
            tmp_res = ''
            for line in fp:
                if not '/home' in line:
                    tmp_res += line
                if config.TESTCASE_RES_DICT[prog_name] in line:  # test pass
                    self.run_res[f'{prog_name}-{prog_type}'] = ''
                    return

            self.run_res[f'{prog_name}-{prog_type}'] = tmp_res

    def gen_wave_rpt(self):
        (prog_name, prog_type) = self.vcs_cfg.prog
        os.chdir(config.VCS_RUN_DIR)

        wave_name = f'{self.dut_cfg.top}_{prog_name}_{prog_type}'
        os.system(f'fsdb2vcd asic_top.fsdb -o {wave_name}.vcd')
        os.system(f'vcd2fst -v {wave_name}.vcd -f {wave_name}.fst')
        os.system(f'tar -czvf {wave_name}.fst.tar.bz2 {wave_name}.fst')

        wave_path = self.gen_wave_dir()
        os.system(f'cp -rf {wave_name}.fst.tar.bz2 {wave_path}')

        cmd = f'curl -k -F "file=@{wave_name}.fst.tar.bz2"'
        with open(f'{config.TEMPLATE_DIR}/wave.token', 'r',
                  encoding='utf-8') as fp:
            for v in fp:
                if 'upload_cli' in v:
                    cmd += f' -X POST {v.rstrip()}'
                else:
                    cmd += f' -F {v.rstrip()}'

        logging.info(msg=f'{cmd}')

        os.system(cmd)
        os.system(f'rm -rf {wave_name}.fst')
        os.system(f'rm -rf {wave_name}.vcd')
        os.system(f'rm -rf {wave_name}.fst.tar.bz2')
        # config.git_commit(
        #     config.WAVE_DIR, '[bot] new wave!',
        #     True)  # NOTE: need to set 'True' when in product env

    def clear_wave_rpt(self):
        pass

    def comp(self):
        os.chdir(config.VCS_RUN_DIR)
        os.system('make comp')
        self.collect_comp_log()

    def run(self):
        os.chdir(config.VCS_RUN_DIR)
        (prog_name, prog_type) = self.vcs_cfg.prog
        if prog_name == 'all':
            for pl in config.TESTCASE_NAME_LIST:
                for mt in config.TESTCASE_TYPE_LIST:
                    self.program(self.dut_cfg.arch, pl, mt)
                    os.system(f'make run test={pl}-{mt}')
                    self.collect_run_log(pl, mt)

        else:
            if self.vcs_cfg.wave == 'off':
                self.program(self.dut_cfg.arch, prog_name, prog_type)
                os.system(f'make run test={prog_name}-{prog_type}')
            else:
                self.vcs_cfg.prog = ('hello', prog_type)  # HACK:
                prog_name = self.vcs_cfg.prog[0]
                self.program(self.dut_cfg.arch, prog_name, prog_type)
                os.system(f'make run test={prog_name}-{prog_type} wave=on')
                self.gen_wave_rpt()
            self.collect_run_log(prog_name, prog_type)

    def gen_rpt_dir(self) -> str:
        rpt_path = f'{config.RPT_DIR}/{self.cmt_cfg.repo}'
        rpt_path += f'/{self.cmt_cfg.date}-{self.cmt_cfg.time}'
        os.system(f'mkdir -p {rpt_path}')
        return rpt_path

    def gen_wave_dir(self) -> str:
        wave_path = f'{config.WAVE_DIR}/{self.cmt_cfg.repo}'
        wave_path += f'/{self.cmt_cfg.date}-{self.cmt_cfg.time}'
        os.system(f'mkdir -p {wave_path}')
        return wave_path

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
        (prog_name, prog_type) = self.vcs_cfg.prog
        with open(f'{rpt_path}/vcs_report', 'a+', encoding='utf-8') as fp:
            fp.writelines(
                '\n#####################\n#vcs program test\n#####################\n'
            )

            if prog_name == 'all':
                for pl in config.TESTCASE_NAME_LIST:
                    for mt in config.TESTCASE_TYPE_LIST:
                        fp.writelines(self.gen_run_res(pl, mt))
            else:
                fp.writelines(self.gen_run_res(prog_name, prog_type))

        return True


vcstest = VCSTest()


def main(cmt_cfg: CommitConfig, dut_cfg: DUTConfig,
         vcs_cfg: VCSConfig) -> bool:
    logging.info(msg='[vcs test]')
    vcstest.clear()
    vcstest.cmt_cfg = cmt_cfg
    vcstest.dut_cfg = dut_cfg
    vcstest.vcs_cfg = vcs_cfg
    vcstest.intg_soc()
    comp_res = True
    vcstest.comp()
    comp_res = vcstest.gen_comp_rpt()

    if comp_res:
        vcstest.run()
        return vcstest.gen_run_rpt()
    return comp_res


if __name__ == '__main__':
    main(CommitConfig('', '', ''), DUTConfig('', '', '', '', ''),
         VCSConfig(25, ('', ''), False))
