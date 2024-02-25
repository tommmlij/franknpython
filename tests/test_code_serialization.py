import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

pythons = {
    "3.9": Path("/Users/tommmlij/miniconda3/envs/plain_python39/bin/python"),
    "3.11": Path("/Users/tommmlij/miniconda3/envs/plain_python311/bin/python")
}


def func1():
    print("Hallo")


def func2():
    print("World")


functions = [func1, func2]


@pytest.fixture(params=pythons)
def python1(request, tmp_path):
    return Python(request.param)


@pytest.fixture(params=pythons)
def python2(request, python1):
    return Python(request.param)


class Python:
    def __init__(self, version):
        print(version)

    def dumps(self, obj):
        print(f"dumps: {obj}")

    def load_and_is_true(self, expression):
        print(f"load: {expression}")


@pytest.mark.parametrize("func", functions)
def test_basic_objects(python1, python2, func):
    python1.dumps(func)
    python2.load_and_is_true(f"obj == {func}")
