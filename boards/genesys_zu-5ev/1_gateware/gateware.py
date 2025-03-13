#! /usr/bin/env python3

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Never, Optional, Sequence

from migen.build.generic_platform import IOStandard, Pins
from migen.build.xilinx.platform import XilinxPlatform
from migen.fhdl.module import Module
from migen.fhdl.structure import ClockDomain, Signal

from zynq_ultra_ps_e_0 import ZynqUltraPsE


class Platform(XilinxPlatform):
    IO = [
        ("pl_leds", 0, Pins("J14"), IOStandard("LVCMOS33")),
        ("pl_leds", 1, Pins("K14"), IOStandard("LVCMOS33")),
        ("pl_leds", 2, Pins("L13"), IOStandard("LVCMOS33")),
        ("pl_leds", 3, Pins("L14"), IOStandard("LVCMOS33")),
    ]

    def __init__(self, platform_zynq_ultra_ps_e_0_0_xci: str):
        super().__init__("xczu5ev-sfvc784-1-e", self.IO, [], name="genesys_zu-5ev", toolchain="vivado")

        self.add_platform_command("set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]")
        self.add_ip(platform_zynq_ultra_ps_e_0_0_xci)

    def create_programmer(self) -> Never:
        raise NotImplementedError()


class Top(Module):
    def __init__(self, platform: Platform, zynq_export: Path):
        super().__init__()

        self.submodules.zynq_ultra_ps_e_0 = ZynqUltraPsE(zynq_export)
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(self.zynq_ultra_ps_e_0.outputs["pl_clk0"])
        self.comb += self.cd_sys.rst.eq(~self.zynq_ultra_ps_e_0.outputs["pl_resetn0"])

        counter = Signal(30)
        self.sync.sys += counter.eq(counter + 1)

        leds = [platform.request("pl_leds", i) for i in range(4)]
        self.comb += [
            leds[0].eq(counter[28]),
            leds[1].eq(counter[26]),
            leds[2].eq(counter[27]),
            leds[3].eq(counter[25]),
        ]


def main(argv: Optional[Sequence[str]] = None) -> None:
    if argv is None:
        argv = sys.argv
    arg_parser = ArgumentParser(prog=argv[0])
    arg_parser.add_argument("-I", "--zynq-ip", default="platform_zynq_ultra_ps_e_0_0.xci")
    arg_parser.add_argument("-Z", "--zynq-export", default="zynq_ultra_ps_e_0")
    arg_parser.add_argument("-B", "--build-dir", default="migen-build")
    arg_parser.add_argument("-N", "--no-run", action="store_true")
    p_args = arg_parser.parse_args(argv[1:])

    platform = Platform(p_args.zynq_ip)
    top_module = Top(platform, Path(p_args.zynq_export))
    platform.build(top_module, build_dir=Path(p_args.build_dir).absolute(), run=not p_args.no_run)


if __name__ == "__main__":
    main()
