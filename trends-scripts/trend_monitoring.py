# Imports
from datetime import datetime
import re
import snscrape.modules.twitter as sntwitter
import time
import urllib.parse


# Ajustando o tempo de monitoramento
intervalo = 1800 # segundos 
tempo_monitorar = 12 # horas
tempo_monitorar = tempo_monitorar * 3600 # (neste caso, 30min)

with open("../trends-data/trends.txt", 'a') as f:
    for i in range(int(tempo_monitorar/intervalo)):
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} \n")
        for tweet in sntwitter.TwitterTrendsScraper().get_items():
            print(str(tweet))
            regexado = re.search("q=.*", str(tweet)).group().replace("q=", '')
            decodificado = urllib.parse.unquote(regexado)
            print(decodificado)
            f.write(f"URL: {tweet} - Trend name: {decodificado} \n")


        time.sleep(intervalo)