from __future__ import annotations
from pathlib import Path
from typing import Awaitable, AsyncIterator
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError


class RemoteImage:
    async def save(
        self, client: ClientSession, dir: Path, forced_name: str = None
    ) -> Awaitable[None]:
        raise NotImplementedError()

    def __eq__(self, image: RemoteImage) -> bool:
        return False

    def __hash__(self) -> int:
        return super().__hash__()


class URLImage(RemoteImage):
    def __init__(self, url: str):
        self.url = url
        self.file_name: str = self.url.rsplit("/", 1)[1]
        assert self.file_name != ""

    def __eq__(self, image: RemoteImage) -> bool:
        if not isinstance(image, URLImage):
            return super().__eq__(image)
        return self.file_name == image.file_name

    def __hash__(self) -> int:
        return hash(self.file_name)

    async def save(
        self, client: ClientSession, dir: Path, forced_name: str = None
    ) -> Awaitable[None]:
        file_name = forced_name or self.file_name
        count = 0
        while count < 3:
            try:
                async with client.get(self.url) as resp:
                    content = await resp.read()
                    assert dir.is_dir()
                    (dir / file_name).write_bytes(content)
                    return
            except ClientError as err:
                #
                pass
            finally:
                count += 1
        # todo: stop system


class ImageSet:
    async def collect(self) -> AsyncIterator[RemoteImage]:
        raise NotImplementedError()

    async def download_all(self, client: ClientSession, dir: Path) -> Awaitable[None]:
        async for image in self.collect():
            await image.save(client, dir)

    def __or__(self, image_set: ImageSet) -> ImageSet:
        return ImageSetUnion(self, image_set)


class ImageSetUnion(ImageSet):
    def __init__(self, image_set1: ImageSet, image_set2: ImageSet):
        self.image_set1 = image_set1
        self.image_set2 = image_set2

    async def collect(self) -> AsyncIterator[RemoteImage]:
        yield from {image async for image in self.image_set1.collect()} | {
            image async for image in self.image_set2.collect()
        }
