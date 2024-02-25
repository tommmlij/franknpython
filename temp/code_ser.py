import asyncio
import inspect

from franknpython.helpers_code import serialize_code


async def serialization():

    def func():
        print("Hallo")

    source = inspect.getsource(func)
    print("in: \n", source)
    source_out = await serialize_code(source)
    print("out: \n", source_out)

if __name__ == '__main__':
    asyncio.run(serialization())