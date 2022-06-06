import requests
import json
import csv
import ast
import yaml

def create_twitter_url():
    handle = "zhusu"
    max_results = 100
    mrf = "max_results={}".format(max_results)
    q = "query=from:{}".format(handle)
    url = "https://api.twitter.com/2/tweets/search/recent?{}&{}".format(
        mrf, q
    )
    return url

def process_yaml():
    with open("Resources/Config.yaml") as file:
        return yaml.safe_load(file)

def create_bearer_token(data):
    return data["search_tweets_api"]["bearer_token"]

def twitter_auth_and_connect(bearer_token, url):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.request("GET", url, headers=headers)
    return response.json()

def create_document_format(res_json):
    data_only = res_json["data"]
    doc_start = '"documents": {}'.format(data_only)
    str_json = "{" + doc_start + "}"
    dump_doc = json.dumps(str_json)
    doc = json.loads(dump_doc)
    return ast.literal_eval(doc)

def convert_json_to_csv(res_json):
    data_file = open('Resources/data_file.csv', 'w')
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

def main():
    url = create_twitter_url()
    data = process_yaml()
    bearer_token = create_bearer_token(data)
    res_json = twitter_auth_and_connect(bearer_token, url)
    convert_json_to_csv(res_json)

if __name__ == "__main__":
    main()