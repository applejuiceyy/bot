from __future__ import annotations

import asyncio
import typing
from functools import partial
from io import BytesIO

import aiofiles
import aiohttp
from PIL import Image
from nextcord.ext import commands

from .exceptions import FlagOpenError


class Flag:
    def __init__(self, url, name, provider, *, is_remote=False):
        self.is_remote = is_remote
        self.provider = provider
        self.name = name
        self.url = url

    async def read(self) -> typing.Optional[bytes]:
        if self.is_remote:
            obj = aiohttp.request("GET", self.url)
        else:
            obj = aiofiles.open(self.url, "rb")

        async with obj as reader:
            return await reader.read()

    async def open(self) -> typing.Optional[Image.Image]:
        data = await self.read()

        if b"<svg" in data:
            # maybe svg
            raise FlagOpenError
        else:
            # maybe raster image
            io = BytesIO(data)

        loop = asyncio.get_running_loop()

        try:
            return await loop.run_in_executor(None, partial(Image.open, io))

        except Exception as e:
            raise FlagOpenError from e

    @classmethod
    async def convert(cls, _, argument) -> Flag:
        from cogs.imaging.flag_retriever import get_flag

        if ":" in argument:
            chunks = argument.split(":")
            ret = await get_flag(chunks[1], chunks[0])
        else:
            ret = await get_flag(argument)

        if ret is None:
            raise commands.BadArgument(f"Flag `{argument}` not found.")

        return ret

    @property
    def safe_url(self):
        if self.is_remote:
            return self.url

        else:
            return "local-file"
