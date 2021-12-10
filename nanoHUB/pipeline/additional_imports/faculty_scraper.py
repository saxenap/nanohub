# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 13:39:40 2020

@author: henry
"""
import os
from googlesearch import search
from bs4 import BeautifulSoup
import urllib
import numpy as np
import matplotlib.pyplot as plt

# %%

class email_name_search:
    def __init__(self,email):
        self.email = email
        
    def g_links(self):
        good = False
        s_index = 0
        while good != True: 
            for j in search(self.email,tld='com',num=1,start=s_index,stop=s_index+1,pause=1):
                print(j)
                url = j
            html = urllib.request.urlopen(url)
            soup = BeautifulSoup(html,'html.parser')
            try: 
                #print(soup.findall('h1')[-1].text)
                print(soup.title.text)
            except:
                print('missing title')
            s_index += 1
            
        return soup.title.text


if __name__ == '__main__':
    t_email = 'vlassovy@fiu.edu'
    t_name = email_name_search(t_email).g_links()
    print(t_name)