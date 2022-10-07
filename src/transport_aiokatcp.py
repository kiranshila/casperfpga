"""
CasperFPGA transport using the aiokatcp backend for talking to KATCP (>=v5) clients.
"""

import aiokatcp
import async_timeout as aio_to

from .transport import Transport
from .casperfpga import CasperFpga

KATCP_PORT = 7147


class KatcpTimeoutError(TimeoutError):
    """
    An error that is raised when a katcp action took
    more than the allocated timeout.
    """

    pass


class KatcpTransport(Transport):
    """A katcp transport client for a casperfpga object using the aiokatcp backend."""

    def __init__(
        self, host: str, parent: CasperFpga, port: int = KATCP_PORT, timeout: int = 10
    ):
        # Setup our class
        self.host = host
        self.port = port
        self.timeout = timeout
        # Init the base class
        Transport.__init__(self, host=host)
        # Create a reference to the parent instance
        # and its logger and its event loop
        self.parent = parent
        self.logger = parent.logger
        self.loop = parent.loop
        # Create and connect to the client
        self.loop.run_until_complete(self._async_connect(host, port, timeout))
        # Either this threw an error, or we've conected
        self.logger.info(
            f"Katcp client - {self.host}:{self.port} created and connected."
        )

    @staticmethod
    async def _async_connect(host: str, port: int, timeout: int) -> aiokatcp.Client:
        async with aio_to.timeout(timeout) as cm:
            client = await aiokatcp.Client.connect(host, port)
        if not cm.expired():
            return client
        else:
            raise KatcpTimeoutError

    @staticmethod
    def test_host_type(host_ip: str, timeout: int = 5):
        """Test if the device at `host_ip` is a katcp client."""
        try:
            KatcpTransport._async_connect(host_ip, KATCP_PORT, timeout)
            return True
        except KatcpTimeoutError:
            return False
