import pytest

from franknpython import __version__
from franknpython.__main__ import main


@pytest.mark.asyncio
async def test_main(capfd):
    await main()
    out, _err = capfd.readouterr()
    assert f'Hi, I am franknpython version {__version__}\n' == out
