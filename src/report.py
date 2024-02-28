#!/bin/python
import os
import logging
import config


class Report(object):
    def __init__(self):
        self.stat = ''


report = Report()


def create_dir(sid: str):
    core_rpt_dir = config.RPT_DIR + '/' + sid
    os.system(f'mkdir -p {core_rpt_dir}')


def gen_state(sid: str, stat: str):
    core_rpt_dir = config.RPT_DIR + '/' + sid
    os.system(f'echo {stat} > {core_rpt_dir}/state')


def main():
    logging.info(msg='[return report]')


if __name__ == '__main__':
    main()
