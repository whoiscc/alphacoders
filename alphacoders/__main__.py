#

from aiohttp import ClientSession
from alphacoders import SingleTask, execute_single_task
import asyncio
from argparse import ArgumentParser

parser = ArgumentParser(description="Download wallpapers from Alpha Coders.")
parser.add_argument("keywords", metavar="keyword", help="searching keywords", nargs="+")
parser.add_argument("--limit", type=int, help="max download wallpaper", default=None)
args = parser.parse_args()

manager_list = [SingleTask(keyword, limit=args.limit) for keyword in args.keywords]


async def main():
    async with ClientSession() as client:
        task_list = [execute_single_task(manager, client) for manager in manager_list]
        [await task for task in task_list]


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
finally:
    for manager in manager_list:
        print(f"[{manager.keyword}] download {manager.complete_count} images")
