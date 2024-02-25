import logging
import asyncio
import inspect
from abc import ABC, abstractmethod

from franknpython.helpers_code import encode_code, decode_code

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


async def serialization():
    class T:

        @staticmethod
        async def func():
            print("Hallo")

    t = T()

    source = inspect.getsource(t.func)
    log.info(f"in: \n{source}")
    source_out = await encode_code(source)
    log.info(f"in: \n{source_out}")
    new_func = await decode_code(source_out)

    class U(ABC):
        encode = staticmethod(new_func)

    u = U()
    await u.encode()


if __name__ == '__main__':
    asyncio.run(serialization())
