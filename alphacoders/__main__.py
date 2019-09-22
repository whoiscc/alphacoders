#

from aiohttp import ClientSession
from alphacoders import SingleTask
import asyncio
from argparse import ArgumentParser

parser = ArgumentParser(description='Download wallpapers from Alpha Coders.')
parser.add_argument('keyword', help='searching keyword')
parser.add_argument('--limit',
                    type=int,
                    help='max download wallpaper',
                    default=None)
args = parser.parse_args()

manager = SingleTask(args.keyword, limit=args.limit)


async def main():
    async with ClientSession() as client:
        await manager.run(client)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
finally:
    print(f'download {manager.complete_count} images')
