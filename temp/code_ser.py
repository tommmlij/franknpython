import logging
import asyncio
import inspect
from abc import ABC, abstractmethod
from pathlib import Path

from franknpython.helpers_code import encode_code, decode_code
from franknpython import OperationBase

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

func = """
async def func(self):
    print("World")
"""


async def serialization():
    class T(OperationBase):
        python = Path(r"C:\Users\tommmlij\.miniconda3\envs\plain_python39\python.exe")
        venv_path = Path()

        @staticmethod
        async def work():
            print("Hallo")

    t = T()

    class U(OperationBase):
        pass

    u = U()

    await t.install()
    await t.run()


if __name__ == '__main__':
    asyncio.run(serialization())
