#!/bin/python

import time
import schedule
import add_soc
import repo_update
import dispatch


# func:
# 1. check code similarity, record commit info(freq, time) -> web
# 2. verilator test
# 3. (iverilog test)
# 4. vcs test
# struct:
# toml, database
def main_task():
    add_soc.main()
    repo_update.main()
    dispatch.main()


schedule.every(1).seconds.do(main_task)

while True:
    schedule.run_pending()
    time.sleep(1)
