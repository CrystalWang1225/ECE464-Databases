#!/usr/bin/env python
# coding: utf-8
# Yuecen Crystal Wang
# ECE 461 Databases
'''
Web scraping tutorial learned from https://towardsdatascience.com/web-scraping-101-in-python-35f8653b1c97
'''
import pandas as pd
import numpy as np
import pymongo
import requests
from requests import get
from bs4 import BeautifulSoup

from time import sleep
from random import randint
from pymongo import MongoClient# Comes with pymongo

client = MongoClient('localhost',27017)
db = client["IMDB_movies"]
actions = db.actions


# Creating the lists we want to write into
titles = []
years = []
imdb_ratings = []
metascores = []
votes = []
run_times=[]
ratings=[]
pages = np.arange(1, 8001, 50)


for page in pages:
    # Getting the contents from the each url
    response = get("https://www.imdb.com/search/title?genres=action&" 
                   + "start=" 
                   + str(page) 
                   + "&explore=title_type,genres&ref_=adv_prv")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Throwing watning for status codes that are not 200
    if response.status_code != 200:
        warn('Request: {}; Status code: {}'.format(requests, response.status_code))

    # Aiming the part of the html we want to get the information from
    movie_div = soup.find_all('div', class_='lister-item mode-advanced')
    
    sleep(randint(2,15))
    
    # To extract the 50 movies on the curent page
    for container in movie_div:
        
        #conditional for all with metascore
        if container.find('div', class_ = 'ratings-metascore') is not None :
            
            # Scraping the movie's name
            name = container.h3.a.text
            titles.append(name)

            #year released
            year = container.h3.find('span', class_= 'lister-item-year text-muted unbold').text
            year = int(year[-5:-1])
            years.append(year)

            #rating
            if container.p.find('span', class_= 'certificate') == None:
                imdb = "N/A"
            else:
                imdb = container.p.find('span', class_= 'certificate').text
            imdb_ratings.append(imdb)

            #runtime
            time = container.p.find('span', class_ = 'runtime').text
            time = int(time.replace(" min", ""))
            run_times.append(time)

             #Metascore
            m_score = container.find('span', class_ = 'metascore').text
            m_score = int(m_score)
            metascores.append(m_score)

            #Number of votes
            vote = container.find('span', attrs = {'name':'nv'})['data-value']
            vote = int(vote)
            votes.append(vote)
            
            # For the rating of the movie
            rating = float(container.strong.text)
            ratings.append(rating)
            
            each_movie = {'movie':name,
                       'year':year,
                       'time(min)':time,
                       'movie_rating':imdb,
                       'metascore':m_score,
                       'vote':vote,
                       'rating': rating}
            result = actions.insert_one(each_movie)
            # print('Each movie document: {0}'.format(result.inserted_id))

# To give an idea of what the dataset look like, a dataframe is created and you can view the dataset by uncommenting the movies.head() line

movies = pd.DataFrame({'movie':titles,
                       'year':years,
                       'time(min)':run_times,
                       'movie_rating':imdb_ratings,
                       'metascore':metascores,
                       'vote':votes,
                       'rating': ratings})

# movies.head()






