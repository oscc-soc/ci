#!/bin/python
import os
from datetime import datetime
from typing import Tuple
import cicd_config
from data_type import CoreInfo, QueueInfo


class CoreQueue(object):
    def __init__(self):
        self.val_list = []

    def clear(self):
        self.val_list.clear()

    def sw_branch(self, bran_name: str):
        cmd = 'git symbolic-ref --short HEAD'
        # check if already in this branch
        cur_bran = cicd_config.exec_cmd(cmd)
        if cur_bran == (bran_name + '\n'):
            return
        else:
            # switch to branch
            print('switch to branch: ' + bran_name)
            cmd = f'git checkout {bran_name}'
            ret = cicd_config.exec_cmd(cmd)
            print(ret)

    # return: (state: Bool, submod_name: str, std_date: str)
    # state: if submod repo has new commit
    def check_remote_update(self, submod_name: str) -> (Tuple[bool, str]):
        os.chdir(cicd_config.SUB_DIR + '/' + submod_name)
        cmd = 'git rev-parse HEAD'
        local_rev = cicd_config.exec_cmd(cmd)

        self.sw_branch(cicd_config.BRANCH_NAME_DEV)
        cmd = 'git remote -v update'
        cicd_config.exec_cmd(cmd)

        cmd = 'git rev-parse origin/HEAD'
        remote_rev = cicd_config.exec_cmd(cmd)

        cmd = f'git log origin/{cicd_config.BRANCH_NAME_DEV}'
        cmd += ' --pretty=format:"%s" -1'
        # print(cmd)
        title_rev = cicd_config.exec_cmd(cmd)

        cmd = f'git log origin/{cicd_config.BRANCH_NAME_DEV}'
        cmd += ' --pretty=format:"%ad" -1'
        # print(date_rev)
        date_rev = cicd_config.exec_cmd(cmd)

        std_date = datetime.strptime(
            date_rev, cicd_config.GMT_FORMAT).strftime(cicd_config.STD_FOMRAT)

        os.chdir(cicd_config.HOME_DIR)
        print(submod_name + ':')
        print(f'local is:       {local_rev}'.rstrip('\n'))
        print(f'remote is:      {remote_rev}'.rstrip('\n'))
        print(f'git info is:    {title_rev}')
        print(f'commit time is: {std_date}')
        return (local_rev != remote_rev, std_date)

    def pull_repo(self, submod_name: str):
        os.chdir(cicd_config.SUB_DIR + '/' + submod_name)
        self.sw_branch(cicd_config.BRANCH_NAME_DEV)

        cmd = 'git pull --progress -v --no-rebase "origin" '
        cmd += cicd_config.BRANCH_NAME_DEV
        ret = cicd_config.exec_cmd(cmd)
        print(ret)
        os.chdir(cicd_config.HOME_DIR)

    def check_repo(self, core_info: CoreInfo):
        ret = self.check_remote_update(core_info.sid)
        # ret = (True, '2022-08-18 09:05:40')
        # restart is also right
        if core_info.flag == 'F':
            print(f'[{core_info.sid}] first! start pull...')
            self.pull_repo(core_info.sid)
            self.val_list.append(QueueInfo(core_info.sid, ret[1]))
        elif ret[0] is True:
            print(f'[{core_info.sid}] changed!! start pull...')
            # self.pull_repo(core_info.sid)
            self.val_list.append(QueueInfo(core_info.sid, ret[1]))
        else:
            print(f'[{core_info.sid}] not changed')

    # os.chdir(cicd_config.HOME_DIR)
    # check if cores have been added to the cicd database
    def check_id(self):
        with open(cicd_config.CORE_LIST_PATH, 'r+', encoding='utf-8') as fp:
            for v in fp.readlines():
                tmp = v.split()
                self.check_repo(CoreInfo('', tmp[0], tmp[1]))

    def update_queue(self):
        # cicd_config.git_commit(cicd_config.SUB_DIR, '[bot] update repo')
        # self.val_list = [('ysyx_23050153', '2022-08-18 09:05:40'),
        #          ('ysyx_23050340', '2022-08-18 09:00:38'),
        #          ('ysyx_23050171', '2022-08-18 09:05:47')]
        self.val_list.sort(key=lambda v: v.date)
        with open(cicd_config.QUEUE_LIST_PATH, 'r+', encoding='utf-8') as fp:
            fp_cores = fp.readlines()
            # print(fp_cores)
            # print(self.val_list)
            # check if new-submit cores are in self.val_list
            for i, va in enumerate(fp_cores):
                for j, vb in enumerate(self.val_list):
                    # print('va: ' + va.split()[0] + ' vb: ' + vb.sid)
                    if va.split()[0] == vb.sid:
                        fp_cores[i] = self.val_list[
                            j].sid + ' ' + self.val_list[j].date + '\n'
                        self.val_list[j].sid = '@'

            for v in self.val_list:
                if v.sid != '@':
                    fp_cores.append(v.sid + ' ' + v.date + '\n')

            # print(fp_cores)
            # print(self.val_list)
            fp.seek(0)
            fp.truncate(0)
            fp.flush()
            fp.writelines(fp_cores)


core_queue = CoreQueue()


def main():
    os.system(f'mkdir -p {cicd_config.DATA_DIR}')
    print('[repo update]')
    core_queue.clear()
    core_queue.check_id()
    core_queue.update_queue()


if __name__ == '__main__':
    main()
