import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import numpy as np
import pandas as pd

class Scrape:
    
    def __init__(self, url, max_page=0):
        self.url = url
        self.max_page = max_page
        self.domain_name = 'https://{}'.format(link.split('/')[2])
    
    def getSoup(self, link):
        source_code = requests.get(link)
        plain_text = source_code.text
        return(BeautifulSoup(plain_text, 'html.parser'))
    
    def last_page(self):
        soup = self.getSoup(self.url)
        last_pn = soup.find('a', {'class':'pageNum last'})
        return int(last_pn.get('data-page-number'))
            
    def craw(self):
        page = 1
        review_data = defaultdict(list)
        if self.max_page == 0:
            self.max_page = self.last_page()
        while page <= self.max_page:
            soup  = self.getSoup(self.url)
            rs = soup.findAll('div', {'class':'reviewSelector'})
            for review in rs:
                review_data['Site'].append(self.url)
                
                title = review.find('span', {'class':'noQuotes'})
                review_data['Review_Title'].append(title.string)
            
                date = review.find('span', {'class':'ratingDate'})
                review_data['Review_Date'].append(date.get('title'))
            
                para = review.find('p', {'class':'partial_entry'})                
                if ('more' in ((para.text.split()[-1]).lower())):
                    title = review.find('a', {'class':'title'})
                    href =('https://www.tripadvisor.in{}'.format(title.get('href')))
                    self.get_review_details(href, review_data)
                else:
                    review_data['Review_Paragraph'].append(para.text)
            
                r = review.find('div', {'class':'ui_column is-9'})
                temptext = str(r.select('div > span')[0])
                review_data['Rating'].append(temptext[-11])
            
            page+=1
            next_page = soup.find('a', {'data-page-number':str(page)})
            self.url = '{}{}'.format(self.domain_name, next_page.get('href'))
        return review_data    
    
    def get_review_details(self, title_link, review_data):
        soup = Scrape.getSoup(self, title_link)
        rs = soup.find('div', {'class':'reviewSelector'})
        for review in rs:
            para = review.find('p', {'class':'partial_entry'})
            review_data['Review_Paragraph'].append(para.text)


class SaveAsExcel:
    
    def __init__(self, op_dict, name):
        self.name = name
        self.op_dict = op_dict
    
    def save_file(self):
        data = pd.DataFrame(self.op_dict)
        data.to_excel('{}.xlsx'.format(self.name), index=False)


if __name__ == '__main__':
	link = input('Enter URL: ')
	npage = int(input('Number of Pages (For all pages = 0): '))
	web_scrape = Scrape(link, npage)
	data_dict = web_scrape.craw()
	SaveAsExcel(data_dict, 'ReviewData').save_file()