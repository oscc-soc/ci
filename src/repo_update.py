#!/bin/python
import os
import logging
from datetime import datetime
import pickle
from typing import Tuple
import config
import config_parser
import report
from data_type import DUTInfo, QueueInfo


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
        os.chdir(f'{config.SUB_DIR}/{submod_name}')
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
    def check_repo(self, dut_info: DUTInfo):
        ret = self.check_remote_update(dut_info.repo)
        # restart is also right
        if dut_info.flag == 'F':
            logging.info(msg=f'[{dut_info.repo}] first! start pull...')
            self.pull_repo(dut_info.repo)
            report.create_dir(dut_info.repo)
            parse_res = config_parser.main(dut_info.repo)
            if parse_res[0] is True:
                self.sub_list.append(
                    QueueInfo(dut_info.repo, ret[1],
                              config_parser.submit_config()))
            else:
                report.gen_state(parse_res[1])
                config.git_commit(config.RPT_DIR, '[bot] update state file',
                                  True)

        elif ret[0] is True:
            logging.info(msg=f'[{dut_info.repo}] changed!! start pull...')
            self.pull_repo(dut_info.repo)
            report.create_dir(dut_info.repo)
            parse_res = config_parser.main(dut_info.repo)
            if parse_res[0] is True:
                self.sub_list.append(
                    QueueInfo(dut_info.repo, ret[1],
                              config_parser.submit_config()))
            else:
                report.gen_state(parse_res[1])
                config.git_commit(config.RPT_DIR, '[bot] update state file',
                                  True)
        else:
            logging.info(msg=f'[{dut_info.repo}] not changed')

    # check if cores have been added to the cicd database
    def check_id(self):
        logging.info('[check id]')
        with open(config.DUT_LIST_PATH, 'r', encoding='utf-8') as fp:
            for v in fp:
                dut_info = v.split()
                self.check_repo(DUTInfo('', dut_info[0], dut_info[1]))

    def update_queue(self):
        logging.info('[update queue]')
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
                    if va.repo == vb.repo:
                        self.old_sub_list[i] = self.sub_list[j]
                        self.sub_list[j].repo = '@'

            for v in self.sub_list:
                if v.repo != '@':
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
