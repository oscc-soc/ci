#!/bin/python
import os
import logging
from typing import Tuple
import config


# helper class
class Report(object):
    def __init__(self):
        self.dut_rpt_dir = ''


report = Report()


def create_dir(repo: str):
    report.dut_rpt_dir = f'{config.RPT_DIR}/{repo}'
    os.system(f'mkdir -p {report.dut_rpt_dir}')


def send_mail(notif_cfg: Tuple[str, str],
              commit: str,
              flag: str,
              state_desc: str = ''):
    (rcpt_mail_url, send_ena) = notif_cfg
    if send_ena == 'on':
        cmd = 'curl --url smtp://smtp.qq.com'
        cmd += f' --mail-from {config.SEND_MAIL_URL}'
        cmd += f' --mail-rcpt {rcpt_mail_url}'
        os.system(
            f'cp -rf {config.TEMPLATE_DIR}/mail.{flag} {config.DATA_DIR}/tmp_mail.{flag}'
        )

        config.repl_str(f'{config.DATA_DIR}/tmp_mail.{flag}',
                        'TEMPLATE_SEND_MAIL_URL', config.SEND_MAIL_URL)

        config.repl_str(f'{config.DATA_DIR}/tmp_mail.{flag}',
                        'TEMPLATE_RCPT_MAIL_URL', rcpt_mail_url)

        config.repl_str(f'{config.DATA_DIR}/tmp_mail.{flag}', 'TEMPLATE_NAME',
                        rcpt_mail_url.split('@')[0])

        config.repl_str(f'{config.DATA_DIR}/tmp_mail.{flag}',
                        'TEMPLATE_COMMIT', commit)

        if flag == 'state':
            config.repl_str(f'{config.DATA_DIR}/tmp_mail.{flag}',
                            'TEMPLATE_STATE', state_desc)

        cmd += f' --upload-file {config.DATA_DIR}/tmp_mail.{flag}'
        with open(f'{config.TEMPLATE_DIR}/mail.token', 'r',
                  encoding='utf-8') as fp:
            for v in fp:
                cmd += f' --user {v.rstrip()}'
        print(cmd)
        os.system(cmd)


def gen_state(stat: str):
    os.system(f'echo {stat} > {report.dut_rpt_dir}/state')


def main():
    logging.info(msg='[return report]')
    send_mail('maksyuki@126.com', '2024-03-11-09:52:51', 'info')


if __name__ == '__main__':
    main()
