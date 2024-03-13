#!/bin/python

import re
from typing import Tuple
from enum import Enum


def find_str(file: str, pat: str) -> Tuple[bool, int]:
    cnt = 0
    with open(file, 'r', encoding='utf-8') as fp:
        for line in fp:
            cnt += 1
            if re.match(pat, line):
                print(f'{str(cnt)}: {line}')
                return (True, cnt)
    return (False, 0)


file_path = '/home/liaoyuchi/Desktop/ysyx_ci_env/ysyx_ci_result/submit/'
file_path += 'ysyx_22000000/ysyx_22000000.v'
top = 'ysyx_22000000'
clk = 'clock'

(top_state, top_pos) = find_str(file_path,
                                f'\\s*module\\s*{top}\\s*[\\(\\)|\\(|\\s*]')

if top_state is False:
    print('error')

if find_str(file_path, f'\\s*{clk}\\s*')[0] is False:
    print('error')
else:
    print('right')


class LogState(Enum):
    start = 0
    end = 1


file_path = '/home/liaoyuchi/Desktop/ysyx_ci_env/ysyx_ci_result/submit/'

lint = []
warn = []
err = []
log_state = [LogState.end, LogState.end, LogState.end]
with open(f'{file_path}/../../vcs/run/compile.log', 'r',
          encoding='utf-8') as fp:
    for line in fp:
        if line[0:4] == 'Lint':
            log_state[0] = LogState.start
        elif line[0:7] == 'Warning':
            log_state[1] = LogState.start
        elif line[0:5] == 'Error':
            log_state[2] = LogState.start
        elif line == '\n':
            log_state = [LogState.end, LogState.end, LogState.end]
        if log_state[0] == LogState.start:
            lint.append(line)
        elif log_state[1] == LogState.start:
            warn.append(line)
        elif log_state[2] == LogState.start:
            err.append(line)

print(len(lint))
print(len(warn))
print(len(err))

if len(lint) == 0 and len(warn) == 0 and len(err) == 0:
    print('all clear')
else:
    print('error')