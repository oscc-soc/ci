#!/bin/python

import os
import logging
import pickle
import config
import config_parser
# import iv_test
# import ver_test
import vcs_test
import dc_test
# import wave_test


def create_dir(sid: str):
    core_rpt_dir = config.RPT_DIR + '/' + sid
    os.system(f'mkdir -p {core_rpt_dir}')
    os.system(f'echo state: under test > {core_rpt_dir}/state')


class Dispatch(object):
    def __init__(self):
        self.sub_list = []

    def clear(self):
        self.sub_list = []

    def parse(self) -> bool:
        with open(config.QUEUE_LIST_PATH, 'rb') as fp:
            self.sub_list = pickle.load(fp)
            if len(self.sub_list) == 0:
                return False

        # pop first queue info and dispatch tasks
        sub_cfg = self.sub_list[0].sub_cfg
        # only dut pass vcs test, then it can be test by dc flow
        if sub_cfg.dut_cfg.commit == '':
            if vcs_test.main(sub_cfg['dut'], sub_cfg['vcs']) is True:
                dc_test.main(sub_cfg['dut'], sub_cfg['dc'])
        elif sub_cfg.dut_cfg.commit == 'vcs':
            vcs_test.main(sub_cfg['dut'], sub_cfg['vcs'])
        elif sub_cfg.dut_cfg.commit == 'dc':
            dc_test.main(sub_cfg['dut'], sub_cfg['dc'])

        del self.sub_list[0]
        return True


dispatch = Dispatch()


# dispatch different task according to the config.toml
def main():
    logging.info('[dispatch task]')

    dispatch.clear()
    if dispatch.parse() is False:
        logging.info(msg='this is not core in queue')


if __name__ == '__main__':
    main()
