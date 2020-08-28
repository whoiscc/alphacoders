#

from aiohttp.client_exceptions import ClientError
from lxml import html
from pathlib import Path
from asyncio import create_task
from functools import wraps


def start_immediately(task):
    @wraps(task)
    def wrapper(*args, **kwargs):
        return create_task(task(*args, **kwargs))

    return wrapper


@start_immediately
async def download_page(client, url):
    count = 0
    while True:
        print(f"(retry = {count}) download url: {url}")
        try:
            async with client.get(url) as resp:
                assert resp.status == 200
                return await resp.text()
        except ClientError:
            pass
        finally:
            count += 1


@start_immediately
async def download_image(client, url, target_dir, name):
    count = 0
    while True:
        print(f"(retry = {count}) download image: {url} -> {target_dir / name}")
        try:
            async with client.get(url) as resp:
                content = await resp.read()
                target_dir.mkdir(exist_ok=True)
                (target_dir / name).write_bytes(content)
                return
        except ClientError:
            pass
        finally:
            count += 1


def download_search(client, keyword, page):
    safe_keyword = keyword.replace(" ", "+")
    # url = f"https://mobile.alphacoders.com/by-resolution/5?search={safe_keyword}&page={page}"
    url = f"https://wall.alphacoders.com/search.php?search={safe_keyword}&page={page}"
    return download_page(client, url)


@start_immediately
async def query_image_id(client, keyword=None, page=None, document=None):
    if document is None:
        assert keyword is not None and page is not None
        search = await download_search(client, keyword, page)
        document = html.fromstring(search)
    a_list = document.xpath('//div[@class="boxgrid"]/a')
    href_list = [a.attrib["href"] for a in a_list]
    return href_list


def query_page_count(document):
    count_string = document.xpath('//ul[@class="pagination"]/li[last() - 1]/a/text()')[
        0
    ]
    return int(count_string)


@start_immediately
async def query_image_url(client, detail_path):
    url = f"https://wall.alphacoders.com/{detail_path}"
    detail = await download_page(client, url)
    document = html.fromstring(detail)
    image = document.xpath('//div[@class="center img-container-desktop"]/a')[0]
    return image.attrib["href"]


@start_immediately
async def download_image_by_id(manager, client, image_id, target_dir):
    image_url = await query_image_url(client, image_id)
    name = image_url.split("/")[-1]
    await download_image(client, image_url, target_dir, name)
    manager.complete_count += 1


class SingleTask:
    def __init__(self, keyword, limit=None):
        self.keyword = keyword
        self.limit = limit
        self.complete_count = 0
        self.triggered = False

    async def run(self, client):
        assert not self.triggered
        self.triggered = True

        first_search_doc = html.fromstring(
            await download_search(client, self.keyword, 1)
        )
        page_count = query_page_count(first_search_doc)
        download_image_task_list = []
        image_count = 0
        for page in range(1, page_count + 1):
            if page == 1:
                partial_list = await query_image_id(client, document=first_search_doc)
            else:
                partial_list = await query_image_id(
                    client, keyword=self.keyword, page=page
                )
            if self.limit is not None:
                partial_list = partial_list[: self.limit - image_count]
            image_count += len(partial_list)

            for image_id in partial_list:
                download_image_task_list.append(
                    download_image_by_id(self, client, image_id, Path(self.keyword))
                )

            if self.limit is not None and image_count == self.limit:
                break

        for task in download_image_task_list:
            await task


@start_immediately
async def execute_single_task(manager, client):
    return await manager.run(client)
