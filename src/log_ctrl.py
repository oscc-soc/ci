#!/bin/python

import os
import glob
import config


def save_run_log():
    # save_log_[xx]
    file_list = glob.glob(f'{config.SAVE_LOG_PATH}*')
    if len(file_list) == 0:
        os.system(f'cp -rf {config.RUN_LOG_PATH} {config.SAVE_LOG_PATH}_0')

    else:
        max_idx = 0
        for v in file_list:
            idx = int(v.split('_')[-1])
            if idx > max_idx:
                max_idx = idx

        os.system(
            f'cp -rf {config.RUN_LOG_PATH} {config.SAVE_LOG_PATH}_{max_idx+1}')

    os.system(f'echo "" > {config.RUN_LOG_PATH}')


def main():
    if os.path.isfile(config.RUN_LOG_PATH):
        file_size = os.path.getsize(config.RUN_LOG_PATH)
        if file_size >= config.RUN_LOG_SIZE_LIMIT:
            save_run_log()


if __name__ == '__main__':
    main()
