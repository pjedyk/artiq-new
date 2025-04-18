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

    client = create_client(workspace=p_args.workspace_dir)

    if "hw_pf" not in map(itemgetter("name"), client.list_components()):
        client.create_platform_component(
            "hw_pf",
            p_args.hw_design,
            cpu="psu_cortexr5_0",
            advanced_options=client.create_advanced_options_dict(user_dtsi=p_args.user_dtsi),
        )
    hw_pf = client.get_component("hw_pf")
    assert isinstance(hw_pf, Platform)

    # TODO: Update HW

    xfsbl_ddr_init_left = SCRIPT_HOME / "xfsbl_ddr_init.c"
    xfsbl_ddr_init_right = Path(p_args.workspace_dir) / "hw_pf" / "zynqmp_fsbl" / "xfsbl_ddr_init.c"
    if not filecmp.cmp(xfsbl_ddr_init_left, xfsbl_ddr_init_right):
        xfsbl_ddr_init_right.write_bytes(xfsbl_ddr_init_left.read_bytes())

    if "app" not in map(itemgetter("name"), client.list_components()):
        client.create_app_component("app", _path_to(p_args.workspace_dir, "hw_pf", "export", "hw_pf", "hw_pf.xpfm"))
    app = client.get_component("app")
    assert isinstance(app, HostComponent)

    src_files = list(map(attrgetter("name"), Path(p_args.src_dir).glob("*.[chS]")))
    app.import_files(p_args.src_dir, src_files, "src")
    app.set_app_config("USER_LINK_DIRECTORIES", [p_args.rust_fw_dir])
    app.set_app_config("USER_LINK_LIBRARIES", ["rust_firmware"])

    hw_pf.build()
    app.build()


if __name__ == "__main__":
    main()
