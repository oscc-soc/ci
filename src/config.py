#!/bin/python

# Copyright (c) 2023 Beijing Institute of Open Source Chip
# archinfo is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#             http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import os
import re
import logging

BRANCH_NAME_DEV = 'master'

GMT_FORMAT = '%a %b %d %H:%M:%S %Y %z'
STD_FOMRAT = '%Y-%m-%d %H:%M:%S'

CUR_BRAN = '202403'
# CUR_BRAN = 'main'  # NOTE: just for test
HOME_DIR = f'{os.getcwd()}'
DATA_DIR = f'{HOME_DIR}/../data/{CUR_BRAN}'
SUBMIT_LIST_PATH = f'{DATA_DIR}/submit_list'
DUT_LIST_PATH = f'{DATA_DIR}/dut_list'
QUEUE_LIST_PATH = f'{DATA_DIR}/queue_list'
RUN_LOG_PATH = f'{DATA_DIR}/run.log'
SAVE_LOG_PATH = f'{DATA_DIR}/save_log'
# NOTE: need to modify the SUBMIT_DIR path for the CICD repo
# now just for test
SUBMIT_DIR = '/home/liaoyuchi/Desktop/ysyx_ci_env/ysyx_ci_result'
# SUBMIT_DIR = f'{HOME_DIR}/../tests/intg'
SUB_DIR = f'{SUBMIT_DIR}/submit'
RPT_DIR = f'{SUBMIT_DIR}/report'
WAVE_DIR = f'{SUBMIT_DIR}/wave'

# vcs
VCS_DIR = '/home/liaoyuchi/Desktop/ysyx_ci_env/vcs'
VCS_RUN_DIR = f'{VCS_DIR}/run'
VCS_CPU_DIR = f'{VCS_DIR}/cpu'
VCS_SCRIPT_DIR = f'{VCS_DIR}/script'
# dc
DC_SRC_DIR = '/home/liaoyuchi/Desktop/ysyx_ci_env/dc/bes_data/syn/scr'
DC_CFG_DIR = '/home/liaoyuchi/Desktop/ysyx_ci_env/dc/bes_data/common'
DC_LOG_DIR = f'{DC_SRC_DIR}/../log'
DC_RPT_DIR = f'{DC_SRC_DIR}/../rpt'
# template
TEMPLATE_DIR = f'{HOME_DIR}/../template'

TESTCASE_NAME_LIST = ['hello', 'memtest', 'rtthread']
TESTCASE_TYPE_LIST = ['flash', 'mem', 'sdram']
TESTCASE_RES_DICT = {
    'hello': 'Hello World!',
    'memtest': 'ALL TESTS PASSED!!',
    'rtthread': 'Hello RISC-V'
}

RUN_LOG_SIZE_LIMIT = 5 * 1024 * 1024 # 5MB
SEND_MAIL_URL = 'maksyuki@qq.com'

def exec_cmd(cmd: str) -> str:
    try:
        ret = os.popen(cmd).read()
    except Exception as e:
        logging.exception(f"Error '{0}' occured when exec_cmd".format(e))
        ret = ''
    return ret


def find_str(file: str, pat: str) -> bool:
    with open(file, 'r', encoding='utf-8') as fp:
        for line in fp:
            if re.match(pat, line):
                return True
    return False


def repl_str(file: str, old: str, pat: str):
    file_data = ''
    with open(file, 'r', encoding='utf-8') as fp:
        for line in fp:
            if old in line:
                line = line.replace(old, pat)
            file_data += line
    with open(file, 'w', encoding='utf-8') as fp:
        fp.write(file_data)


def git_commit(path: str, info: str, push: bool = False):
    os.chdir(path)
    os.system('git add .')
    os.system(f'git commit -m "{info}"')
    if push:
        os.system('git push')
    os.chdir(HOME_DIR)
