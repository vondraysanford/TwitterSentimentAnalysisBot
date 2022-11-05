import aiohttp
import asyncio
import json
import csv
import ast
import yaml

async def create_twitter_url():
    handle = "elonmusk"
    max_results = 100
    mrf = "max_results={}".format(max_results)
    q = "query=from:{}".format(handle)
    url = "https://api.twitter.com/2/tweets/search/recent?{}&{}".format(
        mrf, q
    )
    return url

async def process_yaml():
    with open("Resources/Config.yaml") as file:
        return yaml.safe_load(file)

async def create_bearer_token(data):
    return data["search_tweets_api"]["bearer_token"]

async def twitter_auth_and_connect(bearer_token, url):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    #response = requests.request("GET", url, headers=headers)
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            twitter_content = await response.content.read()
            twitter_object = json.loads(twitter_content.decode("utf-8"))
            return twitter_object

async def create_document_format(res_json):
    data_only = res_json["data"]
    doc_start = '"documents": {}'.format(data_only)
    str_json = "{" + doc_start + "}"
    dump_doc = json.dumps(str_json)
    doc = json.loads(dump_doc)
    return ast.literal_eval(doc)

async def convert_json_to_csv(res_json):
    data_file = open('Resources/aiohttp_data_file.csv', 'w')
    csv_writer = csv.writer(data_file)
    
    count = 0
    for emp in res_json['data']:
        if count == 0:
            header = emp.keys()
            csv_writer.writerow(header)
            count += 1
        emp['text'] = emp['text'].replace("\n", " ")
        csv_writer.writerow(emp.values())
    
    data_file.close()

async def main():
    url = await create_twitter_url()
    data = await process_yaml()
    bearer_token = await create_bearer_token(data)
    res_json = await twitter_auth_and_connect(bearer_token, url)
    await convert_json_to_csv(res_json)

asyncio.run(main())