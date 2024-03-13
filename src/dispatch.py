#!/bin/python

# import os
import logging
import pickle
import copy
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

        # pop disp_first_cfg queue info and dispatch tasks
        logging.info(msg=f'task queue num: {len(self.sub_list)}')
        disp_first_cfg = copy.deepcopy(self.sub_list[0])
        cmt_cfg = disp_first_cfg.cmt_cfg
        sub_cfg = disp_first_cfg.sub_cfg

        logging.info(msg=f'cmt_cfg: {cmt_cfg}')
        logging.info(msg=f'sub_cfg: {sub_cfg}')
        # update queue state info of other dut
        for i, v in enumerate(self.sub_list):
            report.create_dir(v.cmt_cfg.repo)
            logging.info(msg=f'[dispatch update info]: {v.cmt_cfg.repo}')
            if i == 0:
                report.gen_state('under test')
            else:
                report.gen_state(f'wait {i} duts')

            config.git_commit(config.RPT_DIR, '[bot] update state file', True)

        del self.sub_list[0]
        with open(config.QUEUE_LIST_PATH, 'wb') as fp:
            pickle.dump(self.sub_list, fp)

        # only dut pass vcs test, then it can be test by dc flow
        if sub_cfg.dut_cfg.commit == '':
            if vcs_test.main(cmt_cfg, sub_cfg.dut_cfg, sub_cfg.vcs_cfg):
                dc_test.main(cmt_cfg, sub_cfg.dut_cfg, sub_cfg.dc_cfg)
        elif sub_cfg.dut_cfg.commit == 'vcs':
            vcs_test.main(cmt_cfg, sub_cfg.dut_cfg, sub_cfg.vcs_cfg)
        elif sub_cfg.dut_cfg.commit == 'dc':
            dc_test.main(cmt_cfg, sub_cfg.dut_cfg, sub_cfg.dc_cfg)

        config.git_commit(config.RPT_DIR, '[bot] new report!',
                          True)  # NOTE: need to set 'True' when in product env

        report.send_mail(
            ('maksyuki@126.com', 'on'),
            f'{sub_cfg.dut_cfg.top}-{cmt_cfg.date}-{cmt_cfg.time}')
        report.send_mail(
            sub_cfg.meta_cfg.notif,
            f'{sub_cfg.dut_cfg.top}-{cmt_cfg.date}-{cmt_cfg.time}')
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
