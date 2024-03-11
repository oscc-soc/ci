#!/bin/python

import re
from typing import Tuple


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

(top_state, top_pos) = find_str(file_path, f'\\s*module\\s*{top}\\s*[\\(\\)|\\(|\\s*]')

if top_state is False:
    print('error')

if find_str(file_path, f'\\s*{clk}\\s*')[0] is False:
    print('error')
else:
    print('right')
