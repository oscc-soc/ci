#!/bin/python

import os
import logging
import config
import config_parser
import iv_test
import ver_test
import vcs_test
# import dc_test
# import wave_test


def create_dir(sid: str):
    core_rpt_dir = config.RPT_DIR + '/' + sid
    os.system(f'mkdir -p {core_rpt_dir}')
    os.system(f'echo state: under test > {core_rpt_dir}/state')


def main():
    logging.info('[dispatch task]')
    # extract one file from queue_list
    with open(config.QUEUE_LIST_PATH, 'r+', encoding='utf-8') as fp:
        cores = fp.readlines()
        if cores != []:
            tmp = cores[0].split()
            # print(tmp)
            create_dir(tmp[0])
            res = config_parser.main(tmp[0])
            if res[1] == 'iv':
                iv_test.main()
            elif res[1] == 'ver':
                ver_test.main()
            elif res[1] == 'vcs':
                vcs_test.main()
            elif res[1] == 'dc':
                # dc_test.main()
                pass
        else:
            print('this is not core in queue')


if __name__ == '__main__':
    main()
