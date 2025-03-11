from typing import Optional

from vitis import cli_client

def create_client(
    port: Optional[int] = None, host: str = "localhost", workspace: Optional[str] = None
) -> cli_client.Embedded | cli_client.Accelerated: ...
