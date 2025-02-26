#! /usr/bin/env python3

from migen.build.generic_platform import IOStandard, Pins
from migen.build.xilinx.platform import XilinxPlatform
from migen.fhdl.module import Module
from migen.fhdl.specials import Instance
from migen.fhdl.structure import ClockDomain, Signal


class Platform(XilinxPlatform):
    IO = [
        ("pl_leds", 0, Pins("J14"), IOStandard("LVCMOS33")),
        ("pl_leds", 1, Pins("K14"), IOStandard("LVCMOS33")),
        ("pl_leds", 2, Pins("L13"), IOStandard("LVCMOS33")),
        ("pl_leds", 3, Pins("L14"), IOStandard("LVCMOS33")),
    ]

    CONNECTORS = []

    def __init__(self):
        super().__init__(
            "xczu5ev-sfvc784-1-e",
            self.IO,
            self.CONNECTORS,
            name="genesys_zu-5ev",
            toolchain="vivado",
        )

        self.add_platform_command(
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        )
        self.add_platform_command("set_property DCI_CASCADE {{64}} [get_iobanks 65]")

        self.toolchain.pre_synthesis_commands.extend(
            [
                "create_bd_design system",
                "create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e zynq_ultra_ps_e_0",
                "create_bd_port -dir O -type clk pl_clk0",
                "connect_bd_net [get_bd_pins zynq_ultra_ps_e_0/pl_clk0] [get_bd_pins zynq_ultra_ps_e_0/maxihpm0_lpd_aclk] [get_bd_ports pl_clk0]",
                "save_bd_design",
                "generate_target all [get_files system.bd]",
                "create_ip_run [get_files system.bd]",
                "launch_runs [get_runs system_*synth_1] -jobs 3",
                "wait_on_run [get_runs system_*synth_1]",
                "add_files [make_wrapper -top [get_files system.bd]]",
            ]
        )


class Top(Module):
    def __init__(self, platform: Platform):
        super().__init__()

        self.clock_domains.cd_sys = ClockDomain(reset_less=True)
        self.specials += Instance("system_wrapper", o_pl_clk0=self.cd_sys.clk)

        counter = Signal(26)
        self.sync.sys += counter.eq(counter + 1)

        leds = [platform.request("pl_leds", i) for i in range(4)]
        self.comb += [
            leds[0].eq(counter[25]),
            leds[1].eq(counter[24]),
            leds[2].eq(counter[23]),
            leds[3].eq(counter[22]),
        ]


P = Platform()
M = Top(P)
P.build(M, run=True)
