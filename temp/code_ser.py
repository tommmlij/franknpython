import logging
import asyncio
import inspect
from abc import ABC, abstractmethod

from franknpython.helpers_code import encode_code

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

    class U(ABC):
        @abstractmethod
        async def func(self):
            pass






if __name__ == '__main__':
    asyncio.run(serialization())
