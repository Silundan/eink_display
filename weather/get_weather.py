#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import aiohttp
import asyncio
import json
import time
import glob
import os
import configparser

start_time = time.time()

#reading the config, seperating items with ; - for the cities
conf = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(';')]})
conf.read('/home/pi/eink_display/weather/config.ini')
#getting the API key and cities
OWM_API_key = conf['WEATHER']['OWM_API_key']
cities = conf['WEATHER'].getlist('cities')
data_folder = conf['WEATHER']['project_folder'] + "weather/data/"

#preparing the url for further usage (adding the api in it)
base_url = 'https://api.openweathermap.org/data/2.5/weather?units=metric&appid=' + OWM_API_key + '&q='

#async magic require session & url to work
async def get_weather(session, url):
    async with session.get(url) as response:
        local_weather = await response.json()
        return local_weather

async def main():
    #setting up a session for the fetcher (getweather())
    async with aiohttp.ClientSession() as session:
        #setting up a task list
        tasks = []
        #getting the cities user wanted from variable 'cities'
        for city in cities:
            #generating the url for fetcher
            url = base_url + city
            tasks.append(asyncio.ensure_future(get_weather(session, url)))

        weather_response = await asyncio.gather(*tasks)
        counter = 0

        #purging the old weather data, in case the users changed their mind
        weather_file_path = data_folder + "*.json"
        for jsonpath in glob.iglob(weather_file_path):
            try:
                os.remove(jsonpath)
            except:
                pass
        
        #spitting out the data acquired to individual jsons, file name format: "<counter>_<city name>.json"
        for weather in weather_response:
            file_name = str(counter) + '_' + weather['name'] + '.json'
            file_path = data_folder + file_name
            with open(file_path, 'w') as json_file:
                json.dump(weather, json_file)
            counter += 1

#kicking start the async magic
asyncio.run(main())
print("----- %s seconds -----" % (time.time() - start_time))
