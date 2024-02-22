#!/bin/python

import os
import re
from typing import List
import cicd_config
from data_type import CoreInfo


class Cores(object):
    def __init__(self):
        self.submit_list = []
        self.core_list = []

    def clear(self):
        self.submit_list.clear()
        self.core_list.clear()

    # 1. pattern: ysyx_([0-9]{6})
    # 2. in id list
    def check_valid(self, val: str) -> str:
        if re.match('ysyx_[0-9]{8}', val) is not None:
            return val
        else:
            return ''

    def fill_data(self, term: List[str]):
        self.submit_list.append(CoreInfo(term[0], term[1]))

    def handle_err(self, val: str):
        # NOTE: need to write to the submit info
        print(f'ID: error format, the err val: {val}')

    def add(self):
        with open(cicd_config.SUBMIT_LIST_PATH, 'r+', encoding='utf-8') as fp:
            for v in fp.readlines():
                tmp = v.split()
                # print(tmp[1])
                if self.check_valid(tmp[1]) != '':
                    self.fill_data(tmp)
                else:
                    self.handle_err(tmp)

    # update the core list
    def update(self):
        os.chdir(cicd_config.SUBMIT_DIR)
        # os.system('git checkout ' + cicd_config.CUR_BRAN)
        print(f'git checkout {cicd_config.CUR_BRAN}')
        with open(cicd_config.CORE_LIST_PATH, 'r+', encoding='utf-8') as fp:
            for v in fp.readlines():
                tmp = v.split()
                # print('id: ' + val)
                # filter err and spaces
                if self.check_valid(tmp[0]) != '':
                    self.core_list.append(CoreInfo('', tmp[0]))
                # print('id: ' + v.rstrip('\n'))

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
                print(f'git clone {va.url} submit/{va.sid}')
                new_id.append(CoreInfo('', va.sid, 'F'))

        print(f'new core num: {len(new_id)}')
        self.core_list += new_id
        self.core_list.sort(key=lambda v: v.sid)
        # print(self.core_list)
        with open(cicd_config.CORE_LIST_PATH, 'w+', encoding='utf-8') as fp:
            for v in self.core_list:
                fp.write(v.sid + ' ' + v.flag + '\n')


cores = Cores()


def main():
    print('[add soc]')
    cores.clear()
    cores.add()
    cores.update()


if __name__ == '__main__':
    main()
