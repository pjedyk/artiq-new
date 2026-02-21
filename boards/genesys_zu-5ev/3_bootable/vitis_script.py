#! /bin/false --

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements

import sys
from argparse import ArgumentParser
from filecmp import cmp
from functools import reduce
from operator import attrgetter, itemgetter, truediv
from pathlib import Path
from shutil import copyfile
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
    arg_parser.add_argument("-P", "--platform-xsa", default="platform.xsa")
    arg_parser.add_argument("-D", "--user-dtsi", default=_path_to(SCRIPT_HOME, "system-user.dtsi"))
    arg_parser.add_argument("-S", "--src-dir", default=_path_to(SCRIPT_HOME, "src"))
    arg_parser.add_argument(
        "-R", "--rust-fw-dir", default=_path_to("cargo-build", "armv7r-none-eabihf", "debug")
    )
    p_args = arg_parser.parse_args(argv[1:])

    vitis_ws = Path(p_args.workspace_dir).resolve()
    platform_xsa = Path(p_args.platform_xsa).resolve()
    user_dtsi = Path(p_args.user_dtsi).resolve()
    src_dir = Path(p_args.src_dir).resolve()
    rust_fw_dir = Path(p_args.rust_fw_dir).resolve()

    # SEE: https://docs.amd.com/r/en-US/Vitis-Tutorials-Embedded-Software/Vitis-Embedded-Scripting-Flow
    # SEE: ${XILINX_VITIS}/cli/examples
    client = create_client(workspace=f"{vitis_ws}")

    platform_xsa_local = vitis_ws / "hw_pf" / "hw" / platform_xsa.name
    if platform_xsa_local.exists() and not cmp(platform_xsa, platform_xsa_local):
        client.delete_component("hw_pf")
        client.delete_component("app")

    if "hw_pf" not in map(itemgetter("name"), client.list_components()):
        client.create_platform_component(
            "hw_pf",
            str(platform_xsa),
            cpu="psu_cortexr5_0",
            domain_name="standalone_r5_0",
            advanced_options=client.create_advanced_options_dict(user_dtsi=str(user_dtsi)),
        )
    hw_pf = client.get_component("hw_pf")
    assert isinstance(hw_pf, Platform)
    standalone_r5_0 = hw_pf.get_domain("standalone_r5_0")
    assert isinstance(standalone_r5_0, Domain)

    user_dtsi_local = vitis_ws / "hw_pf" / "hw" / "sdt" / user_dtsi.name
    if not cmp(user_dtsi, user_dtsi_local):
        copyfile(user_dtsi, user_dtsi_local)

    xfsbl_ddr_init_left = SCRIPT_HOME / "xfsbl_ddr_init.c"
    xfsbl_ddr_init_right = vitis_ws / "hw_pf" / "zynqmp_fsbl" / "xfsbl_ddr_init.c"
    if not cmp(xfsbl_ddr_init_left, xfsbl_ddr_init_right):
        copyfile(xfsbl_ddr_init_left, xfsbl_ddr_init_right)

    if "libmetal" not in map(itemgetter("name"), standalone_r5_0.get_libs()):
        standalone_r5_0.set_lib("libmetal")
    if "openamp" not in map(itemgetter("name"), standalone_r5_0.get_libs()):
        standalone_r5_0.set_lib("openamp")

    if "app" not in map(itemgetter("name"), client.list_components()):
        platform_xpfm = client.find_platform_in_repos("hw_pf")
        client.create_app_component("app", platform_xpfm, domain="standalone_r5_0")
    app = client.get_component("app")
    assert isinstance(app, HostComponent)
    ld_file = app.get_ld_script()
    assert isinstance(ld_file, Ldfile)

    src_files = list(map(attrgetter("name"), src_dir.glob("*.[chS]")))
    app.import_files(str(src_dir), src_files, dest_dir_in_cmp="src")
    app.set_app_config("USER_LINK_DIRECTORIES", [str(rust_fw_dir)])
    app.set_app_config("USER_LINK_LIBRARIES", ["rust_firmware"])

    # SEE: system-user.dtsi
    ld_file.update_memory_region("psu_r5_ddr_0_memory_0", "0x3ed00000", "0x40000")

    hw_pf.build()
    app.build()


if __name__ == "__main__":
    main()
