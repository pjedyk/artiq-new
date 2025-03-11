#! /bin/false --

import filecmp
import sys
from argparse import ArgumentParser
from functools import reduce
from operator import itemgetter, truediv
from pathlib import Path
from typing import Optional, Sequence

from vitis import create_client
from vitis.component import HostComponent
from vitis.platform_component import Platform


def _path_to(initial: str, *components: str) -> str:
    return str(reduce(truediv, components, Path(initial)).resolve())


def main(argv: Optional[Sequence[str]] = None) -> None:
    if argv is None:
        argv = sys.argv
    arg_parser = ArgumentParser(prog=argv[0])
    arg_parser.add_argument("-W", "--workspace-dir", default="vitis-ws")
    arg_parser.add_argument("-H", "--hw-design", default="platform.xsa")
    arg_parser.add_argument("-S", "--src-dir", default=_path_to("..", "2_firmware", "src"))
    arg_parser.add_argument("-R", "--rust-fw-dir", default=_path_to("cargo-build", "aarch64-unknown-none", "debug"))
    p_args = arg_parser.parse_args(argv[1:])

    client = create_client(workspace=p_args.workspace_dir)

    if "hw_pf" not in map(itemgetter("name"), client.list_components()):
        client.create_platform_component("hw_pf", p_args.hw_design, cpu="psu_cortexa53_0")
    hw_pf = client.get_component("hw_pf")
    assert isinstance(hw_pf, Platform)

    xfsbl_ddr_init_left = Path(__file__).parent / "xfsbl_ddr_init.c"
    xfsbl_ddr_init_right = Path(p_args.workspace_dir) / "hw_pf" / "zynqmp_fsbl" / "xfsbl_ddr_init.c"
    if not filecmp.cmp(xfsbl_ddr_init_left, xfsbl_ddr_init_right):
        xfsbl_ddr_init_right.write_bytes(xfsbl_ddr_init_left.read_bytes())

    if "app" not in map(itemgetter("name"), client.list_components()):
        client.create_app_component("app", _path_to(p_args.workspace_dir, "hw_pf", "export", "hw_pf", "hw_pf.xpfm"))
    app = client.get_component("app")
    assert isinstance(app, HostComponent)

    app.import_files(p_args.src_dir, ["main.c"], "src")
    app.set_app_config("USER_LINK_DIRECTORIES", [p_args.rust_fw_dir])
    app.set_app_config("USER_LINK_LIBRARIES", ["rust_firmware"])

    hw_pf.build()
    app.build()


if __name__ == "__main__":
    main()
