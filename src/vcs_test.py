#!/bin/python
from enum import Enum
import os
import cicd_config


class LogState(Enum):
    start = 0
    end = 1


class VcsTest(object):
    def __init__(self):
        self.dut = ''
        self.date = ''
        self.time = ''
        self.lint = []
        self.warn = []
        self.err = []

    def clear(self):
        self.dut = ''
        self.date = ''
        self.time = ''
        self.lint = []
        self.warn = []
        self.err = []
        self.clear_dir()

    def clear_dir(self):
        cmd = f'cd {cicd_config.VCS_RUN_DIR}  && make clean'
        cmd += ' && rm temp.fp getReg* novas* verdi* -rf'
        os.system(cmd)
        cmd = f'find {cicd_config.VCS_CPU_DIR}/*'
        cmd += ' grep -v ysyx_210000.v | xargs rm -rf'
        os.system(cmd)

    def intg_soc(self):
        core_path = cicd_config.SUB_DIR + '/' + self.dut
        sv_format = core_path + '.sv'
        v_format = core_path + '.sv'
        if os.path.isfile(sv_format):
            os.system(f'cp {sv_format} {cicd_config.VCS_CPU_DIR}')
        elif os.path.isfile(v_format):
            os.system(f'cp {v_format} {cicd_config.VCS_CPU_DIR}')
        else:
            print('not found core!')

        os.chdir(cicd_config.VCS_SCRIPT_DIR)
        os.system('python autowire.py')
        os.chdir(cicd_config.HOME_DIR)

    def comp(self):
        cmd = f'cd {cicd_config.VCS_RUN_DIR} && make comp'
        os.system(cmd)

        log_state = [LogState.end, LogState.end, LogState.end]
        # NOTE: receive comp log
        with open(cicd_config.VCS_RUN_DIR + '/compile.log',
                  'r',
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
        # err_cnt = 0
        cmd = f'cd {cicd_config.VCS_RUN_DIR} && '
        cmd += 'make all_test'
        os.system(cmd)

    def gen_rpt(self):
        rpt_path = cicd_config.RPT_DIR + '/' + self.dut
        rpt_path += f'/{self.date}-{self.time}'
        os.system(f'mkdir -p {rpt_path}')
        with open(rpt_path + '/vcs_report', 'a+', encoding='utf-8') as fp:
            fp.writelines(f'\ncore: {self.dut}\n')
            fp.writelines(
                '\n################\n#vcs compile log\n################\n'
            )

            if not self.err or not self.warn or not self.lint:
                fp.writelines('all clear\n\n')
            else:
                fp.writelines(self.err + self.warn + self.lint)


vcstest = VcsTest()


def main():
    print('[vcs test]')
    vcstest.clear()
    vcstest.intg_soc()
    vcstest.comp()
    vcstest.run()
    vcstest.gen_rpt()


if __name__ == '__main__':
    main()
