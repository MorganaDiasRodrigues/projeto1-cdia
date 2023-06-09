import json
import re
import snscrape.modules.twitter as sntwitter

path = '../trends-data/trends.txt'
trends = []

with open(path) as f:
    for line in f.readlines():
        trends.append(str(line).rstrip())

for index, item in enumerate(trends):
    if str(item).startswith("D"): # excluindo as datas para termos só URLs e trend name
        trends.remove(trends[index])

trends_existentes = []
trend_text = {}
limit = 15

for item in trends:
    trend_name = re.search("Trend name: (.*)", str(item)).group().replace("Trend name: ", '').rstrip()
    tweets = []
    print("Nome da Trend: ", trend_name)
    if trend_name not in trends_existentes:
        print("Adicionando trend...")
        trends_existentes.append(trend_name)
        for tweet in sntwitter.TwitterSearchScraper(f'{trend_name} lang:en').get_items():
            if len(tweets) == limit:
                print("15 tweets adicionados.")
                break
            else:
                tweets.append([tweet.rawContent])
                trend_text[trend_name] = tweets


with open('../trends-data/tweets-trends.json', 'a') as file:
     file.write(json.dumps(trend_text))