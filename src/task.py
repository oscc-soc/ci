#!/bin/python

import os
import time
import logging
import schedule
import config
import add_dut
import repo_update
import dispatch


# func:
# 1. check code similarity, record commit info(freq, time) -> web
# 2. verilator test
# 3. iverilog test
# 4. vcs test
# struct:
# toml, database
def main_task():
    add_dut.main()
    repo_update.main()
    dispatch.main()


# backup previous version run log
if os.path.isfile(config.RUN_LOG_PATH):
    os.system(f'cp -rf {config.RUN_LOG_PATH} {config.RUN_LOG_PATH}_bp')

# prio level: DEBUG < INFO < WARNING < ERROR < CRITICAL
# logging print message which greater than prio level
logging.basicConfig(filename=config.RUN_LOG_PATH,
                    filemode='a',
                    format='%(asctime)s %(name)s:%(levelname)s:%(message)s',
                    datefmt='%Y-%M-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info('\n=====NEW LOG======\n')  #TODO: add start screen
schedule.every(1).seconds.do(main_task)

while True:
    schedule.run_pending()
    time.sleep(1)
