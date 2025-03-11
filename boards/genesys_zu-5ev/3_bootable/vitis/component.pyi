from typing import Optional, Sequence

class Component:
    def import_files(
        self, from_loc: str, files: Optional[Sequence[str]] = None, dest_dir_in_cmp: Optional[str] = None
    ) -> bool: ...

class BuildSettings(Component):
    def set_app_config(self, key: str, values: Sequence[str]) -> bool: ...

class HostComponent(BuildSettings):
    def build(self) -> int: ...
