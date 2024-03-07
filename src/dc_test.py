#!/bin/python

import os
import re
import logging
import config
from data_type import CommitConfig, DUTConfig, DCConfig


class DCTest(object):
    def __init__(self):
        self.err = []
        self.warn = []
        self.cmt_cfg = CommitConfig('', '', '')
        self.dut_cfg = DUTConfig('', '', '', '')
        self.dc_cfg = DCConfig(100, 'TYP', False)
        self.rpt_path = ''

    def clear(self):
        self.err = []
        self.warn = []
        self.cmt_cfg = CommitConfig('', '', '')
        self.dut_cfg = DUTConfig('', '', '', '')
        self.dc_cfg = DCConfig(100, 'TYP', False)

        os.chdir(config.DC_SRC_DIR)
        os.system(f'cp -rf {config.TEMPLATE_DIR}/dc_run.sh run.sh')
        os.chdir(config.DC_CFG_DIR)
        os.system(f'cp -rf {config.TEMPLATE_DIR}/dc_read_hdl.tcl read_hdl.tcl')
        os.chdir(config.DC_CFG_DIR)
        os.system(f'cp -rf {config.TEMPLATE_DIR}/dc_config.tcl config.tcl')
        os.chdir(config.HOME_DIR)

    def set_para(self):
        # config clk freq and corner
        os.chdir(config.DC_SRC_DIR)
        os.system(
            f'cp -rf {config.TEMPLATE_DIR}/dc_clk.tcl {self.dut_cfg.top}.tcl')
        config.repl_str(f'{self.dut_cfg.top}.tcl', 'TEMPLATE_CLK',
                        self.dut_cfg.clk)
        config.repl_str(f'{self.dut_cfg.top}.tcl', 'TEMPLATE_FREQ',
                        str(self.dc_cfg.freq))
        config.repl_str('run.sh', 'TEMPLATE_TOP', self.dut_cfg.top)
        config.repl_str('run.sh', 'TEMPLATE_CORNER', self.dc_cfg.corner)

        # config retime
        if self.dc_cfg.retime == 'on':
            os.system(
                f'cp -rf {config.TEMPLATE_DIR}/dc_retime_flow.tcl flow_com/syn_common_flow.tcl')
        else:
            os.system(
                f'cp -rf {config.TEMPLATE_DIR}/dc_noretime_flow.tcl flow_com/syn_common_flow.tcl')

        # config hdl read path and top name
        os.chdir(config.DC_CFG_DIR)
        config.repl_str('read_hdl.tcl', 'TEMPLATE_DUT',
                        f'$RTL_PATH/{self.dut_cfg.file}')
        config.repl_str('read_hdl.tcl', 'TEMPLATE_TOP', self.dut_cfg.top)
        config.repl_str('config.tcl', 'TEMPLATE_RTL_PATH',
                        f'{config.SUB_DIR}/{self.cmt_cfg.repo}')
        config.repl_str('config.tcl', 'TEMPLATE_TOP', self.dut_cfg.top)
        os.chdir(config.HOME_DIR)

    def gen_rpt_dir(self) -> str:
        rpt_path = f'{config.RPT_DIR}/{self.cmt_cfg.repo}'
        rpt_path += f'/{self.cmt_cfg.date}-{self.cmt_cfg.time}'
        os.system(f'mkdir -p {rpt_path}')
        return rpt_path

    def run(self):
        os.chdir(config.DC_SRC_DIR)
        os.system('./run.sh')

    def collect_syn_info(self) -> str:
        res = '#####################\nSYNTHESIS INFORMATION\n#####################\n'
        res += f'top: {self.dut_cfg.top}\n'
        res += f'freq: {self.dc_cfg.freq}\n'
        res += f'corner: {self.dc_cfg.corner}\n'
        res += f'retime: {self.dc_cfg.retime}\n'
        return res

    def collect_run_log(self) -> str:
        res = '\n#####################\nRUN LOG\n#####################\n'
        with open(f'{config.DC_LOG_DIR}/{self.dut_cfg.top}.log',
                  'r',
                  encoding='utf-8') as fp:
            for line in fp:
                if re.match('^Error:', line) is not None:
                    self.err.append(line)
                    res += line
                if re.match('^Warning:', line) is not None:
                    self.warn.append(line)
                    res += line
            res += f'****** Message Summary:{len(self.err)} Errors(s) '
            res += f'{len(self.warn)} Warning(s) ******\n'
        return res

    def collect_stat_rpt(self) -> str:
        res = '\n#####################\nSTATISTICS REPORT\n#####################\n'

        with open(f'{self.rpt_path}/{self.dut_cfg.top}.statistics.rpt',
                  'r',
                  encoding='utf-8') as fp:
            res += fp.read()
        return res

    def collect_area_rpt(self) -> str:
        res = '\n#####################\nAREA REPORT\n#####################\n'
        # read area rpt and filter
        with open(f'{self.rpt_path}/{self.dut_cfg.top}.area.rpt',
                  'r',
                  encoding='utf-8') as fp:
            block_filter = False
            for line in fp:
                if block_filter and 'Number of ports' in line:
                    block_filter = False

                if 'Library(s) Used' in line:
                    block_filter = True

                if block_filter is False:
                    res += line

        return res

    def collect_time_rpt(self) -> str:
        res = '\n#####################\nTIME REPORT\n#####################\n'
        # read time rpt and filter
        with open(f'{self.rpt_path}/{self.dut_cfg.top}.timing.rpt',
                  'r',
                  encoding='utf-8') as fp:
            block_filter = False
            for line in fp:
                if 'Des/Clust/Port' in line:
                    block_filter = True

                if block_filter and 'Point' in line:
                    block_filter = False

                if block_filter is False and (not 'Library' in line):
                    res += line
        return res

    def gen_run_rpt(self) -> bool:
        rpt_path = self.gen_rpt_dir()
        with open(f'{rpt_path}/dc_report', 'a+', encoding='utf-8') as fp:
            fp.writelines(self.collect_syn_info())
            fp.writelines(self.collect_run_log())
            fp.writelines(self.collect_stat_rpt())
            fp.writelines(self.collect_area_rpt())
            fp.writelines(self.collect_time_rpt())
        return True


dctest = DCTest()


def main(cmt_cfg: CommitConfig, dut_cfg: DUTConfig, dc_cfg: DCConfig) -> bool:
    logging.info(msg='[dc test]')
    dctest.clear()
    dctest.cmt_cfg = cmt_cfg
    dctest.dut_cfg = dut_cfg
    dctest.dc_cfg = dc_cfg
    dctest.rpt_path = f'{config.DC_RPT_DIR}/{dctest.dut_cfg.top}'
    dctest.set_para()
    dctest.run()
    return dctest.gen_run_rpt()


if __name__ == '__main__':
    main(CommitConfig('', '', ''), DUTConfig('', '', '', ''),
         DCConfig(100, 'TYP', False))
