#! /bin/false --

import filecmp
import sys
from argparse import ArgumentParser
from functools import reduce
from operator import attrgetter, itemgetter, truediv
from pathlib import Path
from typing import Optional, Sequence, Union

from vitis import create_client
from vitis.component import HostComponent
from vitis.domain import Domain
from vitis.ldfile import Ldfile
from vitis.platform_component import Platform

SCRIPT_HOME = Path(__file__).parent


def _path_to(initial: Union[Path, str], *components: str) -> str:
    return str(reduce(truediv, components, Path(initial)).resolve())


def main(argv: Optional[Sequence[str]] = None) -> None:
    if argv is None:
        argv = sys.argv
    arg_parser = ArgumentParser(prog=argv[0])
    arg_parser.add_argument("-W", "--workspace-dir", default="vitis-ws")
    arg_parser.add_argument("-H", "--hw-design", default="platform.xsa")
    arg_parser.add_argument("-D", "--user-dtsi", default=_path_to(SCRIPT_HOME, "user.dtsi"))
    arg_parser.add_argument("-S", "--src-dir", default=_path_to(SCRIPT_HOME, "src"))
    arg_parser.add_argument("-R", "--rust-fw-dir", default=_path_to("cargo-build", "armv7r-none-eabihf", "debug"))
    p_args = arg_parser.parse_args(argv[1:])

    # SEE: https://docs.amd.com/r/en-US/Vitis-Tutorials-Embedded-Software/Vitis-Embedded-Scripting-Flow
    # SEE: Xilinx/2025.1/Vitis/cli/examples
    client = create_client(workspace=p_args.workspace_dir)

    # TODO: Update HW

    if "hw_pf" not in map(itemgetter("name"), client.list_components()):
        client.create_platform_component(
            "hw_pf",
            p_args.hw_design,
            cpu="psu_cortexr5_0",
            domain_name="standalone_r5_0",
            advanced_options=client.create_advanced_options_dict(user_dtsi=p_args.user_dtsi),
        )
    hw_pf = client.get_component("hw_pf")
    assert isinstance(hw_pf, Platform)

    xfsbl_ddr_init_left = SCRIPT_HOME / "xfsbl_ddr_init.c"
    xfsbl_ddr_init_right = Path(p_args.workspace_dir) / "hw_pf" / "zynqmp_fsbl" / "xfsbl_ddr_init.c"
    if not filecmp.cmp(xfsbl_ddr_init_left, xfsbl_ddr_init_right):
        xfsbl_ddr_init_right.write_bytes(xfsbl_ddr_init_left.read_bytes())

    standalone_r5_0 = hw_pf.get_domain("standalone_r5_0")
    assert isinstance(standalone_r5_0, Domain)

    if "libmetal" not in map(itemgetter("name"), standalone_r5_0.get_libs()):
        standalone_r5_0.set_lib("libmetal")
    if "openamp" not in map(itemgetter("name"), standalone_r5_0.get_libs()):
        standalone_r5_0.set_lib("openamp")
    standalone_r5_0.set_config("lib", "OPENAMP_WITH_PROXY", "true", lib_name="openamp")

    if "app" not in map(itemgetter("name"), client.list_components()):
        platform_xpfm = client.find_platform_in_repos("hw_pf")
        client.create_app_component("app", platform_xpfm, domain="standalone_r5_0")
    app = client.get_component("app")
    assert isinstance(app, HostComponent)

    src_files = list(map(attrgetter("name"), Path(p_args.src_dir).glob("*.[chS]")))
    app.import_files(p_args.src_dir, src_files)
    app.set_app_config("USER_LINK_DIRECTORIES", [p_args.rust_fw_dir])
    app.set_app_config("USER_LINK_LIBRARIES", ["rust_firmware"])

    ld_file = app.get_ld_script()
    assert isinstance(ld_file, Ldfile)

    # SEE: common/petalinux/meta-petalinux-artiq/recipes-bsp/device-tree/files/zynqmp-openamp.dtsi
    ld_file.update_memory_region("psu_r5_ddr_0_memory_0", "0x3ed00000", "0x40000")

    hw_pf.build()
    app.build()


if __name__ == "__main__":
    main()
