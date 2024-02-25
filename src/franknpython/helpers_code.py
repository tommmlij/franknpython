import re
import logging
from types import CodeType, FunctionType


log = logging.getLogger()


async def decode_code(data) -> FunctionType:
    code_obj = compile(data, '<string>', 'exec')
    work_function = FunctionType(
        next((const for const in code_obj.co_consts if isinstance(const, CodeType))),
        globals())

    return work_function


async def encode_code(code: str) -> str:
    # Align left
    i_length = len(code)
    code = code.lstrip(" ")
    pattern = r"(^|\n) {" + str(i_length - len(code)) + r"}"
    code = re.sub(pattern, '\n', code)

    log.debug(f"1:\n{code}")

    # Remove blank lines
    code = re.sub(r'\n[\n ]*\n', '\n', code)

    log.debug(f"2:\n{code}")

    # Remove header
    code = re.sub(r'^\s*@staticmethod\s*\n', '', code)

    log.debug(f"3:\n{code}")

    return code
