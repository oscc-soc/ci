#!/bin/python

import os
import re
import logging
from typing import List
import config
from data_type import CoreInfo


class Cores(object):

    def __init__(self):
        self.submit_list = []
        self.core_list = []

    def clear(self):
        self.submit_list.clear()
        self.core_list.clear()

    # 1. pattern: ysyx_([0-9]{8})
    # 2. pattern: ysyx_([0-9]{6})
    # 3. in id list
    def check_valid(self, val: str) -> str:
        if re.match('ysyx_[0-9]{8}', val) is not None:
            return val
        elif re.match('ysyx_[0-9]{6}', val) is not None:
            return val
        else:
            return ''

    def fill_data(self, term: List[str]):
        self.submit_list.append(CoreInfo(term[0], term[1]))

    def handle_err(self, val: str):
        # NOTE: need to write to the submit info
        logging.info(msg=f'ID: error format, the err val: {val}')

    def add(self):
        with open(config.SUBMIT_LIST_PATH, 'r+', encoding='utf-8') as fp:
            for v in fp.readlines():
                tmp = v.split()
                logging.debug(msg=tmp[1])
                if self.check_valid(tmp[1]) != '':
                    self.fill_data(tmp)
                else:
                    self.handle_err(tmp)

    # update the core list
    def update(self):
        os.chdir(config.SUBMIT_DIR)
        os.system('git checkout ' + config.CUR_BRAN)
        logging.info(msg=f'git checkout {config.CUR_BRAN}')
        with open(config.CORE_LIST_PATH, 'r+', encoding='utf-8') as fp:
            for v in fp.readlines():
                tmp = v.split()
                # filter err and spaces
                if self.check_valid(tmp[0]) != '':
                    self.core_list.append(CoreInfo('', tmp[0]))
                logging.debug(msg=f'id: {tmp[0]}')

        self.core_list.sort(key=lambda v: v.sid)
        self.submit_list.sort(key=lambda v: v.sid)

        new_id = []
        for va in self.submit_list:
            is_find = False
            for vb in self.core_list:
                if va.sid == vb.sid:
                    is_find = True
                    break

            if is_find is False:
                os.system(f'git clone {va.url} submit/{va.sid}')
                logging.debug(msg=f'git clone {va.url} submit/{va.sid}')
                new_id.append(CoreInfo('', va.sid, 'F'))

        logging.debug(msg=f'new core num: {len(new_id)}')
        self.core_list += new_id
        self.core_list.sort(key=lambda v: v.sid)
        logging.debug(msg=self.core_list)
        with open(config.CORE_LIST_PATH, 'w+', encoding='utf-8') as fp:
            for v in self.core_list:
                fp.write(v.sid + ' ' + v.flag + '\n')


cores = Cores()


def main():
    logging.info(msg='[add soc]')
    os.system(f'mkdir -p {config.DATA_DIR}')
    cores.clear()
    cores.add()
    cores.update()


if __name__ == '__main__':
    main()
