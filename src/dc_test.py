#!/bin/python

import os
import re
# import argparse
import logging
import time
# import datetime
import config
from data_type import DUTConfig, DCConfig

freqlist = ['100']
for freq in freqlist:
    with open(config.DC_SRC_DIR + '/asic_top/ysyx_229998.tcl',
              encoding='utf-8') as fp:
        message = ''
        for line in fp:
            line = re.sub('u0_rcg/u0_pll/CLK_OUT (\d+)',
                          'u0_rcg/u0_pll/CLK_OUT {freq_p}'.format(freq_p=freq),
                          line)
            message += line
    with open(config.DC_SRC_DIR + '/asic_top/ysyx_229998.tcl',
              'w',
              encoding='utf-8') as fp:
        fp.write(message)

    vtlist = ['SVT40+LVT40']
    # user0  = time.strftime('%Y_%m_%d_%H:%M:%S')
    date = time.strftime('%Y_%m_%d_%H:%M:%S')
    user0 = 'CICD_YSYX_'
    proc = 'SIMC(110nm)'
    track = '8T'
    s = '_'
    f = 'M'
    top_name = 'ysyx_229998'
    for vt in vtlist:
        corner_list = ['MAX']
        for corner in corner_list:
            user = user0 + freq + f + s + vt + s + track + corner
            os.system(
                'run_syn -d ysyx_229998 -c {corner_p} -t {track_p} -v {vt_p} -u {user_p} -n smic110'
                .format(corner_p=corner, track_p=track, vt_p=vt, user_p=user))
            # os.system(
            # './report_filter -d ysyx_229998 -u {user_p}'.format(user_p=user))
            os.chdir(config.DC_LOG_DIR)
            print(f'Current working directory: {0}'.format(os.getcwd()))

            user_name = top_name + '_' + user
            user_name_txt = user_name + '.txt'
            result_name = '../out/dc_report_' + user_name_txt
            error_log = '../out/error_log_' + user_name_txt
            error_log2 = '../out/error_log2_' + user_name_txt
            warning_log = '../out/warning_log_' + user_name_txt
            warning_log2 = '../out/warning_log2_' + user_name_txt

            area_rpt = f'../rpt/{0}/{1}'.format(user_name,
                                                top_name) + '.area.rpt'
            area_rpt2 = f'../out/{0}'.format(user_name) + '2.area.rpt'
            timing_rpt = f'../rpt/{0}/{1}'.format(user_name,
                                                  top_name) + '.timing.rpt'
            timing_rpt2 = f'../out/{0}'.format(user_name) + '2.timing.rpt'
            final_rpt = '../out/' + user_name_txt
            log_name = user_name + '.log'

            with open(result_name, 'w', encoding='utf-8') as fp:
                text = '             SYNTHESIS REPORT\n\n==============Information==============\n'
                text += f'commit date: {0}\ntop_name: {1}\nfoundry: {2}\n'.format(
                    date, top_name, proc)
                text += f'corner: {0}\ntrack: {1}\nvoltage channel: {2}\n'.format(
                    corner, track, vt)
                text += '\n==============ERROR & WARNING==============\nErrors\n'
                fp.write(text)

            # f_error = open(error_log, 'w')
            # # os.remove(error_log)
            i = 1
            print(log_name)
            with open(log_name, 'r', encoding='utf-8') as fp:
                data = fp.readlines()
                for line in data:
                    # print(line)
                    pattern = re.compile(r'^Error:.*')
                    string = str(line)
                    url = re.findall(pattern, string)
                    with open(error_log, 'a+', encoding='utf-8') as fp2:
                        for urls in url:
                            fp2.write(urls + '\n')

            with open(error_log, 'r', encoding='utf-8') as fp:
                message = ''
                for line in fp:
                    line = re.sub(
                        "Error: Value for list 'object_list' must have 1 elements.",
                        "DEFAULT:", line)
                    line = re.sub(
                        "Error: Can't find lib_cells matching (.*)'.",
                        "DEFAULT:", line)
                    line = re.sub(
                        "Error: Could not open (.*).svf for writing.",
                        "DEFAULT:", line)
                    line = re.sub(
                        "Error: Unable to open DDC file (.*) for writing. (DDC-1)",
                        "DEFAULT:", line)
                    line = re.sub("Error: Write command failed.", "DEFAULT:",
                                  line)
                    message += line
            with open(error_log2, 'w+', encoding='utf-8') as fp:
                fp.write(message)

            with open(error_log2, 'r', encoding='utf-8') as fp:
                data = fp.readlines()
                for line in data:
                    pattern = re.compile(r'^Error:.*')
                    string = str(line)
                    url = re.findall(pattern, string)
                    with open(result_name, 'a+', encoding='utf-8') as fp2:
                        for urls in url:
                            fp2.write(f'{0}'.format(i) + '. ' + urls + '\n')
                            i += 1

            with open(result_name, 'a', encoding='utf-8') as fp:
                fp.write('\nWarnings\n')

            # f_warning = open(warning_log, 'w', encoding='utf-8')
            # os.remove(warning_log)
            j = 1

            with open(log_name, 'r', encoding='utf-8') as fp:
                data = fp.readlines()

                for line in data:
                    pattern = re.compile(r'^Warning:.*')
                    string = str(line)
                    url = re.findall(pattern, string)
                    with open(warning_log, 'a+', encoding='utf-8') as fp2:
                        for urls in url:
                            fp2.write(urls + '\n')

            with open(warning_log, 'r', encoding='utf-8') as fp:
                message = ''
                for line in fp:
                    line = re.sub(
                        "Warning: Clock group CLK_clock_others_1 has all design clocks in one group.",
                        "DEFAULT:", line)
                    line = re.sub(
                        "Warning: The trip points for the library named (.*) differ from those in the library named (.*).",
                        "DEFAULT: (TIM-164)", line)
                    line = re.sub(
                        "Warning: The specified replacement character \(_\) is conflicting with the specified allowed or restricted character.",
                        "DEFAULT:", line)
                    message += line
            with open(warning_log2, 'w+', encoding='utf-8') as fp:
                fp.write(message)

            with open(warning_log2, 'r', encoding='utf-8') as fp:
                data = fp.readlines()

                for line in data:
                    pattern = re.compile(r'^Warning:.*')
                    string = str(line)
                    url = re.findall(pattern, string)
                    with open(result_name, 'a+', encoding='utf-8') as fp2:
                        for urls in url:
                            fp2.write(f'{0}'.format(j) + '. ' + urls + '\n')
                            j = j + 1

            with open(result_name, 'a', encoding='utf-8') as fp:
                tmp = '\n\n****** Message Summary: '
                tmp += f'{0} Error(s), {1} Warning(s) ******'.format(
                    i - 1, j - 1)
                fp.write(tmp)

            os.chdir(config.DC_RPT_DIR)
            print(f'Current working directory: {0}'.format(os.getcwd()))

            rpt_name = user_name + '/' + top_name + '.statistics.rpt'
            with open(result_name, 'a', encoding='utf-8') as fp:
                text = '\n'
                fp.write(text)

            with open(rpt_name, 'r', encoding='utf-8') as fp:
                data = fp.readlines()

            timing_flag = False
            timing_pass = True
            for line in data:
                pattern = re.compile(r'.*')
                string = str(line)
                url = re.findall(pattern, string)
                with open(result_name, 'a+', encoding='utf-8') as fp:
                    for urls in url:
                        fp.write(urls + '\n')

                if 'Timing' in line:
                    timing_flag = True

                if timing_flag and re.match('CLK', line) is not None:
                    timing_info = line.split()
                    if float(timing_info[3]) < 0 or float(timing_info[4]) < 0:
                        timing_pass = False

            with open(result_name, 'a+', encoding='utf-8') as fp:
                if timing_pass:
                    fp.write('\n\nf=100Mhz PASS!!!')
                else:
                    fp.write('\n\nf=100Mhz FAIL!!!')

            os.chdir(config.DC_SRC_DIR)

            with open(result_name, 'a', encoding='utf-8') as fp:
                txt = '\n\n================AREA REPORT================\n\n'
                fp.write(txt)

            with open(area_rpt, 'r', encoding='utf-8') as fp:
                message = ''
                for line in fp:
                    line = re.sub('Library\(s\) Used:', '', line)
                    line = re.sub('scc011ums_hd_lvt_ss_v1p08_125c_ccs(.*)', '',
                                  line)
                    line = re.sub('S011HD1P_X32Y2D128_SS_1.08_125(.*)', '',
                                  line)
                    line = re.sub('Version:(.*)', '', line)
                    message += line
            with open(area_rpt2, 'w+', encoding='utf-8') as fp:
                fp.write(message)

            with open(area_rpt2, 'r', encoding='utf-8') as fp:
                data = fp.readlines()

            for line in data:
                pattern = re.compile(r'.*')
                string = str(line)
                url = re.findall(pattern, string)
                with open(result_name, 'a+', encoding='utf-8') as fp:
                    for urls in url:
                        fp.write(urls + '\n')

            with open(result_name, 'r', encoding='utf-8') as file1:
                with open(final_rpt, 'w', encoding='utf-8') as file2:
                    for line in file1.readlines():
                        if line == '\n':
                            line = line.strip('\n')
                        file2.write(line)
            os.system('cp ' + final_rpt + ' ../out/dc_report')

            print(f'Current working directory: {0}'.format(os.getcwd()))
            # os.remove(error_log)
            # os.remove(error_log2)
            # os.remove(warning_log)
            # os.remove(warning_log2)
            # os.remove(area_rpt2)
            # os.remove(result_name)


class DCTest(object):
    def __init__(self):
        self.dut_cfg = DUTConfig('', '', '', '')
        self.dc_cfg = DCConfig(100, 'TYP', False)

    def clear(self):
        os.chdir(config.DC_SRC_DIR)
        os.system('cp -rf tm_run.sh run.sh')
        os.chdir(config.DC_CFG_DIR)
        os.system('cp -rf tm_read_hdl.tcl read_hdl.tcl')
        os.chdir(config.DC_CFG_DIR)
        os.system('cp -rf tm_config.tcl config.tcl')
        os.chdir(config.HOME_DIR)

    def set_para(self):
        # config clk freq and corner
        os.chdir(config.DC_SRC_DIR)
        os.system(f'cp -rf template.tcl {self.dut_cfg.top}.tcl')
        config.repl_str(f'{self.dut_cfg.top}.tcl', 'TEMPLATE_CLK',
                        self.dut_cfg.clk)
        config.repl_str(f'{self.dut_cfg.top}.tcl', 'TEMPLATE_FREQ',
                        self.dc_cfg.freq)
        config.repl_str('run.sh', 'TEMPLATE_TOP', self.dut_cfg.top)
        config.repl_str('run.sh', 'TEMPLATE_CORNER', self.dc_cfg.corner)

        # config retime
        if self.dc_cfg.retime == 'on':
            os.system(
                'cp -rf flow_com/retime.tcl flow_com/syn_common_flow.tcl')
        else:
            os.system(
                'cp -rf flow_com/no_retime.tcl flow_com/syn_common_flow.tcl')

        # config hdl read path and top name
        os.chdir(config.DC_CFG_DIR)
        config.repl_str('read_hdl.tcl', 'TEMPLATE_DUT',
                        f'$RTL_PATH/{self.dut_cfg.file}')
        config.repl_str('read_hdl.tcl', 'TEMPLATE_TOP', self.dut_cfg.top)
        config.repl_str('config.tcl', 'TEMPLATE_DUT',
                        f'{config.SUB_DIR}/{self.dut_cfg.top}')
        config.repl_str('config.tcl', 'TEMPLATE_TOP', self.dut_cfg.top)
        os.chdir(config.HOME_DIR)

    def run(self):
        os.chdir(config.DC_SRC_DIR)
        os.system('./run.sh')


dctest = DCTest()


def main(dut_cfg: DUTConfig, dc_cfg: DCConfig) -> bool:
    logging.info(msg='[dc test]')
    dctest.clear()
    dctest.dut_cfg = dut_cfg
    dctest.dc_cfg = dc_cfg
    dctest.set_para()
    dctest.run()
    

    return True


if __name__ == '__main__':
    main(DUTConfig('', '', '', ''), DCConfig(100, 'TYP', False))
