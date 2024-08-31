import os
import aiohttp
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from tavily import TavilyClient
import requests
import string
from parsel import Selector
from rich.console import Console
from rich.table import Table
from pick import pick
from pydantic import BaseModel
from urllib.parse import urlparse
import asyncio

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


class Sentiment(BaseModel):
    sentiment: str
    confidence_score: float


def create_table(company):
    table = Table(title=f"{company} Earnings Report Analysis", show_lines=True)
    table.add_column("Reporter", style="cyan")
    table.add_column("Sentiment", style="magenta")
    table.add_column("Confidence Score", style="blue")
    return table


def cleanup_string(input_string):
    cleaned_string = input_string.strip()
    cleaned_string = " ".join(cleaned_string.split())
    cleaned_string = "".join(filter(lambda x: x in string.printable, cleaned_string))
    return cleaned_string


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            domain_name = urlparse(url).netloc
            resp = await response.text()
            parsed_resp = BeautifulSoup(resp, "html.parser")
            return {
                "domain_name": domain_name,
                "text": parsed_resp.get_text().replace("\n", ""),
            }

async def analyzer(company, table):
    response = tavily_client.search(
        f"{company} earnings report", topic="news", max_results=20
    )
    urls = [i["url"] for i in response["results"]]

    results = []
    console = Console()
    with console.status("[bold green]Analyzing...[/bold green]", spinner="dots"):
        tasks = [fetch(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        for res in responses:

            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst. You are given a string of text and you need to extract the sentiment from it. You need to return a json object with the sentiment and the confidence score. The confidence score is a number between 0 and 1. The sentiment is a string that is either 'positive', 'negative' or 'neutral'.",
                    },
                    {"role": "user", "content": res["text"]},
                ],
                response_format=Sentiment,
            )
            result_dict = completion.choices[0].message.parsed.model_dump()
            result_dict["domain_name"] = res["domain_name"]
            results.append(result_dict)

    for result in results:
        table.add_row(
            result["domain_name"],
            result["sentiment"],
            str(result["confidence_score"]),
            style=(
                "green"
                if result["sentiment"] == "positive"
                else "red" if result["sentiment"] == "negative" else "yellow"
            ),
        )
    console.print(table)


def earnings_today():
    req = requests.get("https://www.marketbeat.com/earnings/latest/")
    resp = Selector(text=req.text)
    options = [
        tab.xpath(".//td[1]/a/div[3]/text()").get()
        for tab in resp.xpath('//table[@class="scroll-table sort-table"]/tbody/tr')
    ]
    title = "Please choose a company to analyze: "
    option, index = pick(options, title, indicator="=>", default_index=0)
    table = create_table(option)
    asyncio.run(analyzer(option, table))


if __name__ == "__main__":
    earnings_today()
