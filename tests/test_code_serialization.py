import asyncio
import inspect
from pathlib import Path

import pytest

from franknpython import OperationBase

pythons = [
    "3.9",
    "3.11"
]

interpreters = {
    "3.9": Path(r"C:\Users\tommmlij\.miniconda3\envs\plain_python39\python.exe"),
    "3.11": Path(r"C:\Users\tommmlij\.miniconda3\envs\plain_python311\python.exe")
}


def func1():
    print("Hallo")


def func2():
    print("World")


functions = [func1, func2]


@pytest.fixture(params=pythons)
def python1(request, tmp_path):
    class Python1(OperationBase):
        python = request.param
        venv_path = tmp_path

    return Python1()


@pytest.fixture(params=pythons)
def python2(request, tmp_path):
    class Python1(OperationBase):
        python = request.param
        venv_path = tmp_path

    return Python1()


@pytest.mark.asyncio
@pytest.mark.parametrize("func", functions)
async def test_basic_objects(python1, python2, func):
    await python1.import_work(inspect.getsource(func))

