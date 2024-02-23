import pickle
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Any


class EncoderBase(ABC):

    @abstractmethod
    async def encode(self, stuff, file):
        pass

    @abstractmethod
    async def decode(self, file):
        pass

    async def _encode(self, stuff: Any, file: Path):
        return await self.encode(stuff, file)

    async def _decode(self, file: Path):
        return await self.decode(file)


class PickleEncoder(EncoderBase):

    async def encode(self, stuff, file):
        with open(file, 'wb') as f:
            f.write(stuff)

    async def decode(self, file):
        with open(file, 'rb') as f:
            return pickle.load(f)
