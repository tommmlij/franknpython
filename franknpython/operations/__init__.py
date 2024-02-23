import inspect
import pathlib
import importlib.util
import sys

from franknpython.operations.base import OperationBase


def create_operation(operation_name):
    assert operation_name in __all__
    return globals()[operation_name]


ops = ["create_operation"]

path = pathlib.Path(__file__).parent.absolute()
for name in [x for x in path.iterdir() if x.is_dir() and x.stem != "__pycache__" and x.joinpath("main.py").is_file()]:
    p = name.joinpath("main.py").absolute()
    assert p.is_file()
    spec = importlib.util.spec_from_file_location(name.stem, location=p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[name.stem] = module
    spec.loader.exec_module(module)
    cls = None
    for member in inspect.getmembers(module):
        cls = member[1]
        if inspect.isclass(cls) and cls != OperationBase and issubclass(cls, OperationBase):
            requirements = name.joinpath("requirements.txt")
            assert requirements.is_file()
            cls.requirements = requirements
            ops.append(cls.__name__)
            globals()[cls.__name__] = cls

__all__ = ops
