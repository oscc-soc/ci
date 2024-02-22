#!/bin/python
import os

BRANCH_NAME_DEV = 'master'

GMT_FORMAT = '%a %b %d %H:%M:%S %Y %z'
STD_FOMRAT = '%Y-%m-%d %H:%M:%S'

# CUR_BRAN = '202302'
CUR_BRAN = 'main'  # NOTE: just for test
HOME_DIR = os.getcwd() + '/'
DATA_DIR = HOME_DIR + '../data/' + CUR_BRAN
SUBMIT_LIST_PATH = DATA_DIR + '/submit_list'
CORE_LIST_PATH = DATA_DIR + '/core_list'
QUEUE_LIST_PATH = DATA_DIR + '/queue_list'

DC_HOME_DIR = HOME_DIR + '../lib/dc/bes_data/syn/scr'
DC_LOG_DIR = DC_HOME_DIR + '../log'
DC_RPT_DIR = DC_HOME_DIR + '../rpt'
# NOTE: need to modify the SUBMIT_DIR path for the CICD repo
# now just for test
SUBMIT_DIR = HOME_DIR + '../tests/intg'
SUB_DIR = SUBMIT_DIR + '/submit'
RPT_DIR = SUBMIT_DIR + '/report'

VCS_DIR = HOME_DIR + '../vcs'
VCS_RUN_DIR = VCS_DIR + '/run'
VCS_CPU_DIR = VCS_DIR + '/cpu'
VCS_SCRIPT_DIR = VCS_DIR + '/script'


def exec_cmd(cmd: str) -> str:
    try:
        ret = os.popen(cmd).read()
    except Exception as e:
        print(f"Error '{0}' occured when exec_cmd".format(e))
        ret = ''
    return ret


def git_commit(path, info, push=False):
    os.chdir(SUBMIT_DIR)
    os.system('git add ' + path)
    os.system('git commit -m "' + info + '"')
    if push:
        os.system('git push')
    os.chdir(HOME_DIR)
