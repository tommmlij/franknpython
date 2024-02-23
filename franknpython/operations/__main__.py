import asyncio
import pickle
import sys
import traceback
import types
from pathlib import Path

import logging

from franknpython.operations.base import OperationBase, EncoderBase

log = logging.getLogger()


async def main(source):
    with open(Path(source).joinpath("code"), 'r') as code_file:
        code = code_file.read()
        log.debug(f"Code received in script:\n{code}")
    with open(Path(source).joinpath("encoder"), 'r') as encoder_file:
        encoder_code = encoder_file.read()
        log.debug(f"Encoder code received in script:\n{encoder_code}")

    with open(Path(source).joinpath("kwargs"), 'rb') as kwargs_file:
        kwargs = pickle.load(kwargs_file)

    log.debug("code: ", code)
    log.debug("kwargs: ", kwargs)

    code_obj = compile(code, '<string>', 'exec')
    work_function = types.FunctionType(
        next((const for const in code_obj.co_consts if isinstance(const, types.CodeType))),
        globals())

    encoder_code_obj = compile(encoder_code, '<string>', 'exec')
    encode_function = types.FunctionType(
        next((const for const in encoder_code_obj.co_consts if isinstance(const, types.CodeType))),
        globals())

    class Encoder(EncoderBase):
        encode = encode_function

        async def decode(self, file):
            pass  # Just a dummy, we do not decode

    class Surrogate(OperationBase):
        work = staticmethod(work_function)
        encoder = Encoder()

    s = Surrogate()

    result = await s.work_wrapper(**kwargs)

    await s.encoder.encode(result, Path(source_dir).joinpath("result"))


if __name__ == '__main__':

    source_dir = Path(sys.argv[1])
    assert source_dir.is_dir(), f"Directory {sys.argv[1]} does not exist"

    try:
        asyncio.run(main(source_dir))

    except Exception as e:
        log.error(f"{e.__class__.__name__} exception: {str(e)}")
        with open(source_dir.joinpath("error_message"), "w") as f:
            traceback.print_stack(file=f)
            f.write(str(e))
        exit(1)
