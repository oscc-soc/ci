#!/bin/python

import os
# import re
import logging
import config
from data_type import CoreInfo


class DUT(object):
    def __init__(self):
        self.new_dut_list = []
        self.dut_list = []

    def clear(self):
        self.new_dut_list.clear()
        self.dut_list.clear()

    # 1. pattern: ysyx_([0-9]{8})
    # 2. pattern: ysyx_([0-9]{6})
    # 3. in id list
    def check_valid(self, val: str) -> bool:
        return len(val) > 0
        # if re.match('ysyx_[0-9]{8}', val) is not None:
        # return val
        # elif re.match('ysyx_[0-9]{6}', val) is not None:
        # return val
        # else:
        # return ''

    def fill_data(self, url: str, repo: str):
        self.new_dut_list.append(CoreInfo(url, repo))

    def handle_err(self, val: str):
        # NOTE: need to write to the submit info
        logging.info(msg=f'ID: error format, the err val: {val}')

    def add(self):
        with open(config.SUBMIT_LIST_PATH, 'r', encoding='utf-8') as fp:
            for url in fp:
                repo_name = url.split('/')[-1]
                logging.debug(msg=repo_name)
                if self.check_valid(repo_name):
                    self.fill_data(url, repo_name)
                else:
                    self.handle_err(repo_name)

    # update the core list
    def update(self):
        os.chdir(config.SUBMIT_DIR)
        os.system(f'git checkout {config.CUR_BRAN}')
        logging.info(msg=f'git checkout {config.CUR_BRAN}')
        with open(config.DUT_LIST_PATH, 'r', encoding='utf-8') as fp:
            for v in fp:
                repo_name = v.split()[0]
                # filter err and spaces
                if self.check_valid(repo_name):
                    self.dut_list.append(CoreInfo('', repo_name))
                logging.debug(msg=f'repo name: {repo_name}')

        self.dut_list.sort(key=lambda v: v.repo)
        self.new_dut_list.sort(key=lambda v: v.repo)

        new_dut = []
        for va in self.new_dut_list:
            is_find = False
            for vb in self.dut_list:
                if va.repo == vb.repo:
                    is_find = True
                    break

            if is_find is False:
                os.system(f'git clone {va.url} submit/{va.repo}')
                logging.debug(msg=f'git clone {va.url} submit/{va.repo}')
                new_dut.append(CoreInfo('', va.repo, 'F'))

        logging.debug(msg=f'new dut num: {len(new_dut)}')
        self.dut_list += new_dut
        self.dut_list.sort(key=lambda v: v.repo)
        logging.debug(msg=self.dut_list)
        with open(config.DUT_LIST_PATH, 'w+', encoding='utf-8') as fp:
            for v in self.dut_list:
                fp.write(v.repo + ' ' + v.flag + '\n')


dut = DUT()


def main():
    logging.info(msg='[add soc]')
    os.system(f'mkdir -p {config.DATA_DIR}')
    dut.clear()
    dut.add()
    dut.update()


if __name__ == '__main__':
    main()
