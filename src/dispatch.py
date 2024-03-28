#!/bin/python

# Copyright (c) 2023 Beijing Institute of Open Source Chip
# ci is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#             http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.


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
            state_desc = ''
            if i == 0:
                state_desc = 'under test'
            else:
                state_desc = f'wait {i} duts'

            report.gen_state(state_desc)
            config.git_commit(config.RPT_DIR, '[bot] update state file', True)
            report.send_mail(
                v.sub_cfg.meta_cfg.notif,
                f'{v.sub_cfg.dut_cfg.top}-{v.cmt_cfg.date}-{v.cmt_cfg.time}',
                'state', state_desc)

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
            f'{sub_cfg.dut_cfg.top}-{cmt_cfg.date}-{cmt_cfg.time}', 'info')
        report.send_mail(
            sub_cfg.meta_cfg.notif,
            f'{sub_cfg.dut_cfg.top}-{cmt_cfg.date}-{cmt_cfg.time}', 'info')
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
