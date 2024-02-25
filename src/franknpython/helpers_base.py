import asyncio
import inspect
import os
import logging
import pickle
import platform
import re
import subprocess
import sys
from time import time
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile
from types import FunctionType
from typing import Optional
from venv import EnvBuilder
from asyncio import StreamReader
from base64 import urlsafe_b64decode, urlsafe_b64encode

from franknpython.helpers_code import encode_code, decode_code

# from .helpers_code import serialize_code
# from .helpers_io import EncoderBase, PickleEncoder

log_local = logging.getLogger(__name__)


class OperationBase:
    requirements: Optional[Path] = None
    python: Optional[Path] = None
    venv_path: Optional[Path] = None
    install_local_env: bool = False
    encoder: None  # EncoderBase = PickleEncoder()
    _work: Optional[FunctionType]
    _encode: Optional[FunctionType]

    def __init__(self):
        if self.venv_path is None:
            self.venv_path = Path().cwd().joinpath(".venv")

    async def work_wrapper(self, **kwargs):

        class SerializerHandler(logging.StreamHandler):

            def emit(self, record):
                print(urlsafe_b64encode(pickle.dumps(record)).decode("utf-8"))

        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[SerializerHandler()])
        log = logging.getLogger(__name__)

        log.info(f"Hello from {type(self).__name__}, python version is {platform.python_version()}")
        return await self.work(**kwargs)

    @property
    def venv(self) -> Path:
        return self.venv_path.joinpath(type(self).__name__).absolute()

    @property
    def interpreter(self) -> Path:
        python = self.venv.joinpath("Scripts").joinpath("python.exe").absolute()
        assert python.is_file(), f"Missing interpreter at {python.as_posix()}"
        return python

    @property
    def pip(self) -> Path:
        python = self.venv.joinpath("Scripts").joinpath("pip3.exe").absolute()
        assert python.is_file
        return python

    @property
    def activate(self) -> Path:
        python = self.venv.joinpath("Scripts").joinpath("activate.bat").absolute()
        assert python.is_file
        return python

    async def work(self, **kwargs):
        if self._work is None:
            raise NotImplementedError
        return self._work(**kwargs)

    async def import_work(self, code:str) -> None:

        self._work = await decode_code(code)

    async def export_work(self) -> str:
        if self._work is None:
            raise NotImplementedError
        source = inspect.getsource(self._work)
        return await encode_code(source)

    async def encode(self, **kwargs):
        if self._encode is None:
            raise NotImplementedError
        return self._encode(**kwargs)

    async def import_encode(self, code: str) -> None:

        self._encode = await decode_code(code)

    async def export_encode(self) -> str:
        if self._work is None:
            raise NotImplementedError
        source = inspect.getsource(self._encode)
        return await encode_code(source)

    async def run(self, **kwargs):
        async def watch(stream: StreamReader, err=False, pid=os.getpid()):
            _ = err
            async for line in stream:
                if isinstance(line, bytes):
                    # noinspection PyBroadException
                    try:
                        log_pickle = urlsafe_b64decode(line)
                        log_record = pickle.loads(log_pickle)
                        log_record.process = pid
                        log_local.handle(log_record)
                    except Exception:
                        print(line.decode('utf-8'), end="")

        with TemporaryDirectory() as td:
            d = Path(td).absolute()
            log_local.info(
                f"Starting {type(self).__name__} processing via external script in {td}"
            )

            code_file = d.joinpath("code")
            kwargs_file = d.joinpath("kwargs")
            result_file = d.joinpath("result")
            encoder_file = d.joinpath("encoder")

            # Work function source

            source = inspect.getsource(self.work)

            log_local.debug(f"Source from class:\n{source}")

            source = ""  # await serialize_code(source)

            # We inject the kwargs
            source = re.sub(r'((^|\n)async def work(.*):\s*\n)', f'\\1    globals().update({kwargs})\n', source)

            log_local.debug(f"Source edited:\n{source}")

            # Encoder source

            source_encode = inspect.getsource(self.encoder.encode)

            log_local.debug(f"Encoder source from class:\n{source_encode}")

            source_encode = ""  # await serialize_code(source_encode)

            log_local.debug(f"Encoder source edited:\n{source_encode}")

            with open(code_file, 'w') as f:
                f.write(source)
            with open(encoder_file, 'w') as f:
                f.write(source_encode)
            with open(kwargs_file, 'wb') as f:
                pickle.dump(kwargs, f)

            cmd = (
                f"cd {d.as_posix()} && {self.interpreter.as_posix()} -m franknpython.operations {d.as_posix()}"
            )

            start = time()
            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await asyncio.gather(watch(proc.stdout, pid=proc.pid),
                                 watch(proc.stderr, err=True, pid=proc.pid))
            await proc.wait()

            if proc.returncode != 0:
                error_file = d.joinpath("error_message")
                if error_file.exists():
                    with open(error_file, "r") as f:
                        msg = f.read()
                with NamedTemporaryFile(mode="w", delete=False) as tf:
                    tf.write(msg)
                    log_local.warning(
                        f"Processing failed after {time() - start:.2f}seconds with error code {proc.returncode}. "
                        f"Error file: {tf.name}")
                return

            log_local.info(
                f"Processing finished nominally after {time() - start:.2f} seconds"
            )

            if not result_file.is_file():
                return

            return await self.encoder.decode(result_file)

    async def install(self):

        if self.python is not None:
            log_local.debug(f"base_python: {self.python}")
            args = [self.python.as_posix(), '-m', 'venv', self.venv.as_posix()]
            log_local.debug(f"args venv: {args}")
            subprocess.run(args, check=True)
        else:
            log_local.debug(f"Create in {self.venv}")
            builder = EnvBuilder(clear=False,
                                 symlinks=False,
                                 with_pip=True,
                                 upgrade_deps=True)
            builder.create(self.venv)

        this = Path(__file__).parent.parent.parent.absolute().as_posix()

        log_local.debug(f"venv: {self.venv_path}")
        log_local.debug(f"activate: {self.activate}")
        log_local.debug(f"pip: {self.pip}")
        log_local.debug(f"requirements: {self.requirements}")
        log_local.debug(f"target_python: {self.python or sys.executable}")

        log_local.debug(f"this: {this}")

        args = [self.activate.as_posix(),
                '&&', self.interpreter.as_posix(), '-m', 'pip', 'install', '-q', '--no-input', '--upgrade', 'pip']

        if self.install_local_env:
            args.extend(['&&', self.pip.as_posix(), 'install', '-q', '--no-input', this])

        if self.requirements:
            args.extend(['&&', self.pip.as_posix(), 'install', '-q', '--no-input', '-r', self.requirements.as_posix()])

        log_local.debug(f"args: {args}")

        subprocess.run(args, check=True)

    async def update(self):

        this = Path(__file__).absolute().as_posix()

        if self.install_local_env:
            args = [self.activate, '&&', self.pip.as_posix(), 'install', '-q', '--no-input', this]
            log_local.debug(f"args: {args}")
            subprocess.run(args, check=True)
        else:
            log_local.warning(f"{type(self).__name__} is not flagged to install the working dir (*install_local_env*)")
