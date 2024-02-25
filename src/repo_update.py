#!/bin/python
import os
import logging
from datetime import datetime
import pickle
from typing import Tuple
import config
import config_parser
from data_type import CoreInfo, QueueInfo


class CoreQueue(object):
    def __init__(self):
        self.sub_list = []
        self.old_sub_list = []

    def clear(self):
        self.sub_list.clear()
        self.old_sub_list.clear()

    def sw_branch(self, bran_name: str):
        cmd = 'git symbolic-ref --short HEAD'
        # check if already in this branch
        cur_bran = config.exec_cmd(cmd)
        if cur_bran == (bran_name + '\n'):
            return
        else:
            # switch to branch
            logging.info(msg=f'switch to branch: {bran_name}')
            ret = config.exec_cmd(f'git checkout {bran_name}')
            logging.info(msg=ret)

    # return: (state: bool, std_date: str)
    # state: if submod repo has new commit
    def check_remote_update(self, submod_name: str) -> (Tuple[bool, str]):
        os.chdir(config.SUB_DIR + '/' + submod_name)
        cmd = 'git rev-parse HEAD'
        local_rev = config.exec_cmd(cmd)

        self.sw_branch(config.BRANCH_NAME_DEV)
        cmd = 'git remote -v update'
        config.exec_cmd(cmd)

        cmd = 'git rev-parse origin/HEAD'
        remote_rev = config.exec_cmd(cmd)

        cmd = f'git log origin/{config.BRANCH_NAME_DEV}'
        cmd += ' --pretty=format:"%s" -1'
        # print(cmd)
        title_rev = config.exec_cmd(cmd)

        cmd = f'git log origin/{config.BRANCH_NAME_DEV}'
        cmd += ' --pretty=format:"%ad" -1'
        # print(date_rev)
        date_rev = config.exec_cmd(cmd)

        std_date = datetime.strptime(date_rev, config.GMT_FORMAT).strftime(
            config.STD_FOMRAT)

        os.chdir(config.HOME_DIR)
        logging.info(msg=submod_name + ':')
        logging.info(msg=f'local is:       {local_rev}'.rstrip('\n'))
        logging.info(msg=f'remote is:      {remote_rev}'.rstrip('\n'))
        logging.info(msg=f'git info is:    {title_rev}')
        logging.info(msg=f'commit time is: {std_date}')
        return (local_rev != remote_rev, std_date)

    def pull_repo(self, submod_name: str):
        os.chdir(config.SUB_DIR + '/' + submod_name)
        self.sw_branch(config.BRANCH_NAME_DEV)

        cmd = 'git pull --progress -v --no-rebase "origin" '
        cmd += config.BRANCH_NAME_DEV
        ret = config.exec_cmd(cmd)
        print(ret)
        os.chdir(config.HOME_DIR)

    # check if config is valid and parse the config
    def parse_cfg(self):
        pass

    # check if remote repo has been updated
    def check_repo(self, core_info: CoreInfo):
        ret = self.check_remote_update(core_info.sid)
        # restart is also right
        if core_info.flag == 'F':
            logging.info(msg=f'[{core_info.sid}] first! start pull...')
            self.pull_repo(core_info.sid)
            parse_res = config_parser.main(core_info.sid)
            if parse_res[0] is True:
                self.sub_list.append(
                    QueueInfo(core_info.sid, ret[1],
                              config_parser.submit_config()))
            else:
                pass  # TODO: record the error to the submit

        elif ret[0] is True:
            logging.info(msg=f'[{core_info.sid}] changed!! start pull...')
            self.pull_repo(core_info.sid)
            parse_res = config_parser.main(core_info.sid)
            if parse_res[0] is True:
                self.sub_list.append(
                    QueueInfo(core_info.sid, ret[1],
                              config_parser.submit_config()))
            else:
                pass  # TODO: record the error to the submit
        else:
            logging.info(msg=f'[{core_info.sid}] not changed')

    # check if cores have been added to the cicd database
    def check_id(self):
        logging.info('[check id]')
        with open(config.CORE_LIST_PATH, 'r+', encoding='utf-8') as fp:
            for v in fp.readlines():
                tmp = v.split()
                self.check_repo(CoreInfo('', tmp[0], tmp[1]))

    def update_queue(self):
        logging.info('[update queue]')
        # config.git_commit(config.SUB_DIR, '[bot] update repo')
        # self.sub_list = [('ysyx_23050153', '2022-08-18 09:05:40', sub_cfg),
        #          ('ysyx_23050340', '2022-08-18 09:00:38', sub_cfg),
        #          ('ysyx_23050171', '2022-08-18 09:05:47', sub_cfg)]
        self.sub_list.sort(key=lambda v: v.date)
        # check if queue list file exist
        if os.path.isfile(config.QUEUE_LIST_PATH) is False:
            with open(config.QUEUE_LIST_PATH, 'wb') as fp:
                pickle.dump(self.sub_list, fp)
            return

        with open(config.QUEUE_LIST_PATH, 'rb') as fp:
            self.old_sub_list = pickle.load(fp)
            logging.info(msg=self.old_sub_list)
            # check if new-submit cores are in self.sub_list
            for i, va in enumerate(self.old_sub_list):
                for j, vb in enumerate(self.sub_list):
                    if va.sid == vb.sid:
                        self.old_sub_list[i] = self.sub_list[j]
                        self.sub_list[j].sid = '@'

            for v in self.sub_list:
                if v.sid != '@':
                    self.old_sub_list.append(v)

        with open(config.QUEUE_LIST_PATH, 'wb') as fp:
            pickle.dump(self.old_sub_list, fp)


core_queue = CoreQueue()


def main():
    logging.info('[repo update]')
    os.system(f'mkdir -p {config.DATA_DIR}')
    core_queue.clear()
    core_queue.check_id()
    core_queue.update_queue()


if __name__ == '__main__':
    main()
