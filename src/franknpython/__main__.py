import asyncio
import pickle
import sys
import traceback
from pathlib import Path

import aiofiles

from franknpython import OperationBase
from franknpython.helpers_encoder import PickleEncoder


async def main(source):
    import logging

    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()

    async with aiofiles.open(Path(source).joinpath("code"), 'r') as code_file:
        code = await code_file.read()
        log.debug(f"main:Code received in script:\n{code}")
    async with aiofiles.open(Path(source).joinpath("encoder"), 'r') as encoder_file:
        encoder_code = await encoder_file.read()
        log.debug(f"main:Encoder code received in script:\n{encoder_code}")

    with open(Path(source).joinpath("kwargs"), 'rb') as kwargs_file:
        kwargs = pickle.load(kwargs_file)

    log.debug(f"main:code: {code}")
    log.debug(f"main:kwargs: {kwargs}")

    class Surrogate(OperationBase):
        encoder = PickleEncoder()

    s = Surrogate()
    await s.import_work(code)

    result = await s.work_wrapper(**kwargs)

    log.debug(f"main:result: {result}")

    await s.encoder.encode(result, Path(source_dir).joinpath("result"))


if __name__ == '__main__':
    source_dir = Path(sys.argv[1])
    assert source_dir.is_dir(), f"Directory {sys.argv[1]} does not exist"

    try:
        asyncio.run(main(source_dir))

    except Exception as e:
        import logging

        log = logging.getLogger()

        log.error(f"{e.__class__.__name__} exception: {str(e)}")
        with open(source_dir.joinpath("error_message"), "w") as f:
            traceback.print_stack(file=f)
            f.write(str(e))
        exit(1)
