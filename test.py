import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup

async def main():

    urls = [
        "https://example.com/1",
        "https://example.com/2",
        "https://example.com/3",
        "https://example.com/4",
        "https://example.com/5"
    ]

    async def fetch(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.text()
                parsed_resp = BeautifulSoup(resp, "html.parser")
                return parsed_resp.get_text().replace("\n", "")

    tasks = [fetch(url) for url in urls]
    responses = await asyncio.gather(*tasks)

    for i, response in enumerate(responses):
        print(f"Response from {urls[i]}: {response[:100]}")  

if __name__ == "__main__":
    asyncio.run(main())
