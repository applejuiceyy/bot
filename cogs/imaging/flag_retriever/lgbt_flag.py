import typing

import aiohttp

import difflib

from . import Flag
from .abc import FlagRetriever

import urllib.parse


class LGBTFlagRetriever(FlagRetriever):
    @property
    def schema(self):
        return "lgbt"

    async def get_flag(self, name) -> typing.Optional[Flag]:
        async with aiohttp.request("GET", f"https://lgbta.wikia.org/api.php?action=query&"
                                          f"list=search&srsearch={urllib.parse.quote(name)}"
                                          f"&format=json") as search_response:
            json_content = await search_response.json()
            pages = json_content["query"]["search"]

            if pages:
                # there's results; get article image
                first_page_id = pages[0]["pageid"]

                async with aiohttp.request("GET", f"https://lgbta.wikia.org/api.php?action=imageserving&"
                                                  f"wisId={first_page_id}&format=json") as image_response:
                    json_content = await image_response.json()

                    if "error" not in json_content and "image" in json_content:
                        return Flag(json_content["image"]["imageserving"], pages[0]["title"], str(self), is_remote=True)

        return None

    def __str__(self):
        return "lgbt wiki"