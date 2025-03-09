#! /usr/bin/env python3

from functools import reduce
from operator import truediv
from pathlib import Path

from migen.build.generic_platform import IOStandard, Pins
from migen.build.xilinx.platform import XilinxPlatform
from migen.fhdl.module import Module
from migen.fhdl.specials import Instance
from migen.fhdl.structure import ClockDomain, Signal

CWD = Path(".")


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

        self.add_ip(
            reduce(
                truediv,
                [
                    CWD,
                    "vivado-proj",
                    "design.srcs",
                    "sources_1",
                    "bd",
                    "system",
                    "ip",
                    "system_zynq_ultra_ps_e_0_0",
                    "system_zynq_ultra_ps_e_0_0.xci",
                ],
            )
        )

        self.add_platform_command(
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        )


class Top(Module):
    def __init__(self, platform: Platform):
        super().__init__()

        pl_clk0 = Signal()
        pl_resetn0 = Signal()
        self.specials += Instance(
            "system_zynq_ultra_ps_e_0_0", o_pl_clk0=pl_clk0, o_pl_resetn0=pl_resetn0
        )
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(pl_clk0)
        self.comb += self.cd_sys.rst.eq(~pl_resetn0)

        counter = Signal(30)
        self.sync.sys += counter.eq(counter + 1)

        leds = [platform.request("pl_leds", i) for i in range(4)]
        self.comb += [
            leds[0].eq(counter[29]),
            leds[1].eq(counter[28]),
            leds[2].eq(counter[27]),
            leds[3].eq(counter[26]),
        ]


P = Platform()
M = Top(P)
P.build(M, build_dir="migen-build", run=True)
