import json
import sys

import asyncio
import logging
from pathlib import Path

import colorlog

from franknpython import OperationBase, EncoderBase

handler = colorlog.StreamHandler(stream=sys.stdout)
handler.setFormatter(
    colorlog.ColoredFormatter(
        '%(asctime)s - %(process)-5d - %(log_color)s%(levelname)-8s%(reset)s | %(message)s'))

logging.basicConfig(level=logging.DEBUG, handlers=[handler])

log = logging.getLogger()


class Tux(OperationBase):
    requirements = Path().cwd().joinpath("requirements_test1.txt")
    venv_path = Path().cwd().joinpath(".venv")

    @staticmethod
    async def work():
        import cowsay
        t = cowsay.get_output_string('tux', 'Hello World!!')

        return t


class Cow(OperationBase):
    requirements = Path().cwd().joinpath("requirements_test1.txt")
    python = Path('C:/Users/tommmlij/.miniconda3/envs/python_3.9_test/python.exe')

    @staticmethod
    async def work(text="Default text...."):
        import logging
        import cowsay
        logger = logging.getLogger()
        t = cowsay.get_output_string('cow', text=text)
        logger.info(f'Here is your cow:\n{t}')

        return "Juhu!"


async def main():
    ts = [Cow()]
    for t in ts:
        await t.install()
        # await t.update()

    # result_1 = await ts[0].run()
    # log.info(f'Here is your linux user:\n{result_1}')

    result_2 = await ts[0].run(text="WFT, dude!")

    print(type(result_2))
    print(result_2)


async def main2():
    class WhatEver(json.JSONEncoder):
        pass


if __name__ == '__main__':
    asyncio.run(main())
