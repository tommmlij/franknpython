import re
import logging

log = logging.getLogger()


async def serialize_code(code: str) -> str:
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
