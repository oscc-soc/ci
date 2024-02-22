#!/bin/python

import os
from typing import List
import cicd_config

rpt_home = ''
dut_core = ''
lint = ['']
warning = ['']
error = ['']
run_warning = ['']
flag = [0, 0, 0]


def comp_test():
    global lint
    global warning
    global error
    global run_warning
    run_warning.clear()
    global flag
    flag = [0, 0, 0]

    os.system("cd lib/vcs/run && make comp")
    with open("lib/vcs/run/compile.log", 'r', encoding='utf-8') as fp:
        lint.clear()
        warning.clear()
        error.clear()
        for line in fp:
            if flag[0] == 1:
                if 'vga' in line:
                    flag[0] = 0
                    lint.pop()
                    continue
                lint.append(line)
                if line == '\n':
                    lint.append(line)
                    flag[0] = 0
            if flag[1] == 1:
                warning.append(line)
                if line == '\n':
                    warning.append(line)
                    flag[1] = 0
            if flag[2] == 1:
                error.append(line)
                if line == '\n':
                    error.append(line)
                    flag[2] = 0
            elif line[0:4] == 'Lint':
                flag[0] = 1
                lint.append(line)
            elif line[0:7] == 'Warning':
                flag[1] = 1
                warning.append(line)
            elif line[0:5] == 'Error':
                flag[2] = 1
                error.append(line)

    with open(rpt_home + '/vcs_report', 'a+', encoding='utf-8') as fp:
        fp.writelines('\ncore:  ' + dut_core + '\n')
        fp.writelines(
            '\n####################\n#vcs compile log\n####################\n')
        fp.writelines(error + warning + lint)
        if not error and not warning and not lint:
            fp.writelines("\n\n\nall clear!!\n\n\n")

    return (not error) and (not lint)


prog_list = [('hello.flash', 'none', 'hello_test_flash'),
             ('jump.mem', 'hello.mem', 'hello_test_mem'),
             ('jump.sdram', 'hello.sdram', 'hello_test_sdram'),
             ('memtest.flash', 'none', 'memtest_test_flash'),
             ('jump.mem', 'memtest.mem', 'memtest_test_mem'),
             ('jump.sdram', 'memtest.sdram', 'memtest_test_sdram'),
             ('memtest.flash', 'none', 'rtthread_test_flash'),
             ('jump.mem', 'rtthread.mem', 'rtthread_test_mem'),
             ('jump.sdram', 'rtthread.sdram', 'rtthread_test_sdram')]
prog_ret = [False, False, False, False, False, False, False, False, False]


def system_test():
    err_cnt = 0

    with open(rpt_home + '/vcs_report', 'a+', encoding='utf-8') as fp:
        if not error:
            fp.writelines(
                '\n##################\n#vcs system test\n##################\n')

            for i, v in enumerate(prog_list):
                cmd = 'cd lib/vcs/run && '
                cmd += f'ln -sf program/{0} mem_Q128_bottom.vmf '.format(v[0])

                if v[1] != 'none':
                    cmd += f'&& ln -sf program/{0} init_{1}.bin.txt '.format(
                        v[1], v[1].split('.')[1])

                cmd += f'&& make run test={0}'.format(v[2])
                os.system(cmd)

                with open('lib/vcs/run/run.log', 'r', encoding='utf-8') as fp:
                    for line in fp:
                        if flag[1] == 1:
                            run_warning.append(line)
                            if line == '\n':
                                run_warning.append(line)
                                flag[1] = 0
                        if line[0:7] == 'Warning':
                            flag[1] = 1
                            run_warning.append(line)
                        if i < 3 and 'Hello World!' in line:
                            prog_ret[i] = True
                        elif 3 <= i and i < 6 and 'ALL TESTS PASSED!!' in line:
                            prog_ret[i] = True
                        elif 6 <= i and i < 9 and 'Hello RISC-V!' in line:
                            prog_ret[i] = True

            fp.writelines(run_warning)

            for i, v in enumerate(prog_ret):
                (prog_name, _, prog_test) = v.split('_')
                cmd = f'{0} test in {1} '.format(prog_name, prog_test)
                if prog_ret[i]:
                    fp.writelines(cmd + 'pass!!\n')
                else:
                    fp.writelines('!!!' + cmd + 'fail!!!\n')
                    err_cnt += 1

    return err_cnt == 0


def create_rpt_dir() -> bool:
    is_have = False
    with open(cicd_config.QUEUE_LIST_PATH, 'r+', encoding='utf-8') as fp:
        cores = fp.readlines()
        if cores != []:
            # rec's format: ['submit/ysyx_210153', '2022-08-18' '09:05:40']
            rec = cores[0].split()
            global dut_core
            dut_core = rec[0].split('/')[1]

            # record queue state
            os.system('mkdir -p ' + cicd_config.RPT_DIR + dut_core)
            os.system('echo state: under test > ' + cicd_config.RPT_DIR +
                      dut_core + '/state')

            # remove record from queue
            fp.seek(0)
            fp.truncate(0)
            fp.flush()
            fp.writelines(cores[1:])
            is_have = True

            # update other cores state
            fp.seek(0)
            cores = fp.readlines()
            cnt = 1
            for v in cores:
                v_path = cicd_config.RPT_DIR + v.split()[0].split('/')[1]
                os.system('mkdir -p ' + v_path)
                os.system('echo state: wait ' + str(cnt) + ' cores > ' +
                          v_path + '/state')
                cnt += 1

            cicd_config.git_commit(cicd_config.RPT_DIR,
                                   '[bot] update soc state file', True)

            # soc integration
            global rpt_home
            rpt_home = cicd_config.RPT_DIR + dut_core
            rpt_home += '/' + rec[1] + '...' + rec[2]
            os.system('mkdir -p ' + rpt_home)
            soc_intg(rec)
        else:
            print('this is not core in queue')

    return is_have


# rec's format: ['submit/ysyx_210153', '2022-08-18' '09:05:40']
def soc_intg(rec: List[str]):
    core_path = cicd_config.SUBMIT_DIR + rec[0] + '/' + rec[0].split('/')[1]
    v_format = core_path + '.v'
    sv_format = core_path + '.sv'
    if os.path.isfile(v_format):
        os.system('cp ' + v_format + ' lib/vcs/cpu')
    elif os.path.isfile(sv_format):
        os.system('cp ' + sv_format + ' ' + v_format)
        os.system('mv ' + v_format + ' lib/vcs/cpu')
    else:
        print('no core file!')

    # print('cp ' + cicd_config.SUBMIT_DIR  + rec[0] + '/' + rec[0] + '.v')
    os.chdir('lib/vcs/script')
    os.system('python autowire.py')
    os.chdir('../../')


def clean_vcs_env():
    os.system(
        'cd lib/vcs/run && make clean && rm temp.fp getReg* novas* verdi* -rf')
    os.system('find lib/vcs/cpu/* | grep -v ysyx_210000.v | xargs rm -rf')


def clean_dc_env():
    os.chdir(cicd_config.HOME_DIR + 'lib/dc/bes_data/syn/')
    # os.system('rm -rf log/*.log')
    # os.system('rm -rf out/*.txt')
    os.chdir(cicd_config.HOME_DIR)


def run_vcs():
    is_comp_right = comp_test()
    is_run_right = False
    if is_comp_right:
        is_run_right = system_test()
    return is_comp_right and is_run_right


def run_main():
    clean_vcs_env()  # can not move into create_rpt_dir!
    if create_rpt_dir():
        is_vcs_right = run_vcs()
        if is_vcs_right:
            run_dc()
        cicd_config.git_commit(cicd_config.RPT_DIR, '[bot] new report!', True)


def run_dc():
    clean_dc_env()
    os.system('rm -rf lib/vcs/cpu_dc/*.v')
    os.system('cp lib/vcs/cpu/' + dut_core + '.v lib/vcs/cpu_dc/')
    os.chdir('lib/vcs/script')
    os.system('/autowire_new.py')
    os.chdir(cicd_config.HOME_DIR)
    os.chdir('lib/dc/bes_data/syn/scr/')
    os.system('./syn_scr_update')
    os.system('cp ../out/dc_report ' + rpt_home)
    clean_dc_env()
    clean_vcs_env()  # can not move into run_vcs!
    os.chdir(cicd_config.HOME_DIR)


def main():
    print('[ysyx_cicd] SoC Test')
    run_main()


if __name__ == '__main__':
    main()
