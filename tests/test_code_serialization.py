import inspect

import pytest

from franknpython.helpers_code import serialize_code


@pytest.mark.asyncio
async def test_serialization(capfd):

    def func():
        print("Hallo")

    source = inspect.getsource(func)

    source_out = await serialize_code(source)
    assert 1 == source_out, "Bla"
