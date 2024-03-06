#!/bin/python

# import os
import logging
import pickle
import config
import report
# import iv_test
# import ver_test
import vcs_test
import dc_test


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
        logging.info(msg=f'task queue num: {len(self.sub_list)}')
        sub_cfg = self.sub_list[0].sub_cfg
        sub_date = self.sub_list[0].date.split()[0]
        sub_time = self.sub_list[0].date.split()[1]
        logging.info(msg=f'sub_cfg: {sub_cfg}')
        logging.info(msg=f'sub_date: {sub_date}')
        logging.info(msg=f'sub_time: {sub_time}')
        # update queue state info of other dut
        for i, _v in enumerate(self.sub_list):
            if i == 0:
                report.gen_state('under test')
            else:
                report.gen_state(f'wait {i} duts')


        # only dut pass vcs test, then it can be test by dc flow
        if sub_cfg.dut_cfg.commit == '':
            if vcs_test.main(sub_date, sub_time, sub_cfg['dut'],
                             sub_cfg['vcs']) is True:
                dc_test.main(sub_date, sub_time, sub_cfg['dut'], sub_cfg['dc'])
        elif sub_cfg.dut_cfg.commit == 'vcs':
            vcs_test.main(sub_date, sub_time, sub_cfg['dut'], sub_cfg['vcs'])
        elif sub_cfg.dut_cfg.commit == 'dc':
            dc_test.main(sub_date, sub_time, sub_cfg['dut'], sub_cfg['dc'])

        del self.sub_list[0]
        return True


dispatch = Dispatch()


# dispatch different task according to the config.toml
def main():
    logging.info('[dispatch task]')

    dispatch.clear()
    if dispatch.parse() is False:
        logging.info(msg='this is not dut in queue')


if __name__ == '__main__':
    main()
