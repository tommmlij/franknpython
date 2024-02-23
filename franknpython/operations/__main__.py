import asyncio
import pickle
import sys
import traceback
import types
from pathlib import Path

import logging

from franknpython.operations.base import OperationBase

log = logging.getLogger()


async def main(source):
    with open(Path(source).joinpath("code"), 'r') as code_file:
        code = code_file.read()
        log.debug(f"Code received in script:\n{code}")
    with open(Path(source).joinpath("kwargs"), 'rb') as kwargs_file:
        kwargs = pickle.load(kwargs_file)

    log.debug("code: ", code)
    log.debug("kwargs: ", kwargs)

    code_obj = compile(code, '<string>', 'exec')

    new_func_type = types.FunctionType(
        next((const for const in code_obj.co_consts if isinstance(const, types.CodeType))),
        globals())

    class Surrogate(OperationBase):
        work = staticmethod(new_func_type)

    s = Surrogate()
    return await s.work_wrapper(**kwargs)


if __name__ == '__main__':

    source_dir = Path(sys.argv[1])
    assert source_dir.is_dir(), f"Directory {sys.argv[1]} does not exist"

    try:
        result = asyncio.run(main(source_dir))

        with open(Path(source_dir).joinpath("result"), 'wb') as result_file:
            pickle.dump(result, result_file)

    except Exception as e:
        log.error(f"{e.__class__.__name__} exception: {str(e)}")
        with open(source_dir.joinpath("error_message"), "w") as f:
            traceback.print_stack(file=f)
            f.write(str(e))
        exit(1)
