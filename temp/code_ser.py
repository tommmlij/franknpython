import logging
import asyncio
import inspect
import sys
from abc import ABC, abstractmethod
from pathlib import Path

import colorlog

from franknpython.helpers_code import encode_code, decode_code
from franknpython import OperationBase

handler = colorlog.StreamHandler(stream=sys.stdout)
handler.setFormatter(
    colorlog.ColoredFormatter(
        '%(asctime)s - %(process)-5d - %(log_color)s%(levelname)-8s%(reset)s | %(message)s'))

logging.basicConfig(level=logging.DEBUG, handlers=[handler])

log = logging.getLogger()


async def func():
    print("world")


async def serialization():
    class T(OperationBase):
        python = Path(r"C:\Users\tommmlij\.miniconda3\envs\plain_python39\python.exe")
        venv_path = Path().cwd().joinpath(".venv")
        install_local_env = True

        @staticmethod
        async def work():
            print("Hallo")

    t = T()

    class U(OperationBase):
        pass

    u = U()

    await t.install()
    # await t.update()
    await t.run()


if __name__ == '__main__':
    asyncio.run(serialization())
