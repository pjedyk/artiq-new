from typing import Dict, Literal, Optional, Sequence

from vitis.component import HostComponent
from vitis.platform_component import Platform

class Embedded:
    def get_component(self, name: str) -> Platform | HostComponent | object: ...
    def list_components(self) -> Sequence[Dict[str, str]]: ...
    def create_platform_component(
        self,
        name: str,
        hw_design: str,
        desc: Optional[str] = None,
        os: Optional[str] = None,
        cpu: Optional[str] = None,
        domain_name: Optional[str] = None,
        template: Optional[str] = None,
        no_boot_bsp: bool = False,
        fsbl_target: Optional[str] = None,
        fsbl_path: Optional[str] = None,
        pmufw_Elf: Optional[str] = None,
        emu_design: Optional[str] = None,
        platform_xpfm_path: Optional[str] = None,
        is_pmufw_req: bool = False,
        generate_dtb: bool = True,
        advanced_options: Dict[str, str] = {},
    ) -> Platform: ...
    def create_advanced_options_dict(
        self,
        sdt_repo: Optional[str] = None,
        board_dtsi: Optional[str] = None,
        user_dtsi: Optional[str] = None,
        dt_overlay: Optional[Literal["0", "1"]] = None,
        dt_zocl: Optional[Literal["0", "1"]] = None,
    ) -> Dict[str, str]: ...
    def create_app_component(
        self,
        name: str,
        platform: str,
        domain: Optional[str] = None,
        cpu: Optional[str] = None,
        os: Optional[str] = None,
        template: Optional[str] = None,
    ) -> HostComponent: ...

class Accelerated(Embedded): ...
