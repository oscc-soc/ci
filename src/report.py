#!/bin/python
import os
import logging
import config

# helper class
class Report(object):
    def __init__(self):
        self.dut_rpt_dir = ''


report = Report()


def create_dir(sid: str):
    report.dut_rpt_dir = config.RPT_DIR + '/' + sid
    os.system(f'mkdir -p {report.dut_rpt_dir}')


def gen_state(stat: str):
    os.system(f'echo {stat} > {report.dut_rpt_dir}/state')


def main():
    logging.info(msg='[return report]')


if __name__ == '__main__':
    main()