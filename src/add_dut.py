#!/bin/python

import os
# import re
import pickle
import logging
import config
from data_type import DUTInfo


class DUT(object):
    def __init__(self):
        self.all_dut_list = []
        self.old_dut_list = []

    def clear(self):
        self.all_dut_list.clear()
        self.old_dut_list.clear()

    # 1. pattern: ysyx_([0-9]{8})
    # 2. pattern: ysyx_([0-9]{6})
    # 3. in id list
    def check_valid(self, val: str) -> bool:
        return len(val) > 3
        # if re.match('ysyx_[0-9]{8}', val) is not None:
        # return val
        # elif re.match('ysyx_[0-9]{6}', val) is not None:
        # return val
        # else:
        # return ''

    def fill_data(self, url: str, repo: str):
        self.all_dut_list.append(DUTInfo(url, repo))

    def handle_err(self, val: str):
        # NOTE: need to write to the submit info
        logging.info(msg=f'ID: error format, the err val: {val}')

    def add(self):
        with open(config.SUBMIT_LIST_PATH, 'r', encoding='utf-8') as fp:
            for line in fp:
                url = line.rstrip().split()[0]
                repo = line.rstrip().split()[1]
                logging.debug(msg=url)
                logging.debug(msg=repo)
                if self.check_valid(repo):
                    self.fill_data(url, repo)
                else:
                    self.handle_err(repo)

    # update the dut list
    def update(self):
        os.chdir(config.SUBMIT_DIR)
        os.system(f'git checkout {config.CUR_BRAN}')
        logging.info(msg=f'git checkout {config.CUR_BRAN}')
        if os.path.isfile(config.DUT_LIST_PATH):
            with open(config.DUT_LIST_PATH, 'rb') as fp:
                self.old_dut_list = pickle.load(fp)
                for v in self.old_dut_list:
                    logging.debug(msg=f'load dut info: {v}')

        self.old_dut_list.sort(key=lambda v: v.repo)
        self.all_dut_list.sort(key=lambda v: v.repo)

        os.chdir(config.SUB_DIR)
        all_dut = []
        new_dut_num = 0
        for va in self.all_dut_list:
            is_find = False
            for vb in self.old_dut_list:
                if va.repo == vb.repo:
                    is_find = True
                    break

            if is_find is False:
                os.system(f'git clone {va.url} {va.repo}')
                logging.debug(msg=f'git clone {va.url} {va.repo}')
                all_dut.append(DUTInfo(va.url, va.repo, 'F'))
                new_dut_num += 1
            else:
                all_dut.append(va)
        logging.debug(
            msg=f'all dut num: {len(all_dut)} new dut num: {new_dut_num}')
        self.old_dut_list = all_dut
        self.old_dut_list.sort(key=lambda v: v.repo)
        # logging.debug(msg=self.old_dut_list)

        with open(config.DUT_LIST_PATH, 'wb') as fp:
            pickle.dump(self.old_dut_list, fp)


dut = DUT()


def main():
    logging.info(msg='[add soc]')
    os.system(f'mkdir -p {config.DATA_DIR}')
    dut.clear()
    dut.add()
    dut.update()


if __name__ == '__main__':
    main()
