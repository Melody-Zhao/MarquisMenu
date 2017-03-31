import os
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess

# category includes [lunch, brunch, supper]
TsvHeader = ['date', 'day', 'dish', 'category']

def write_to_tsv(item):
    file_path = 'result.tsv'
    if not os.path.isfile(file_path):
        with open(file_path, 'a') as tsv:
            for i in TsvHeader:
                tsv.write(i+'\t')
            tsv.write('\n')
            # unitl now, the header (First row) is ready
    with open(file_path, 'a') as tsv:
        tsv.write('{date}\t{dish}\t{category}\n'.format(
            date=item.date.encode("utf-8"),
            day=item.day.encode("utf-8"),
            dish=item.dish.encode("utf-8"),
            category=item.category.encode("utf-8")
        ))

class Menu(object):
    date = ""
    day = ""
    dish = ""
    category = ""


class MyMenuSpider(scrapy.Spider):
    name = 'example.com'
    start_urls = [
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Feb%2012%20-%20Feb%2018.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Feb%2026%20-%20Mar%204.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Mar%205%20-%2011.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Mar%2012%20-%20Mar%2018.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Mar%2019%20-%20Mar%2025.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Mar%2026%20-%20Apr%201.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Apr%202%20-%208.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Apr%209%20-%2015.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Apr%2016%20-%2022.php',
                'https://www.usask.ca/culinaryservices/plan-your-weekly-marquis-meals/Apr%2023%20-%2029.php']

    def parse(self, response):
        self.logger.info('A response from %s just arrived!', response.url)
        menu_page = BeautifulSoup(response.body, 'lxml')
        div_pattern = re.compile(r'tab-pane fade.*')
        menu_results = menu_page.find_all("div", {'class': div_pattern})
        for every_day_menu in menu_results:

            # for date and day
            date_and_day = every_day_menu.find("div", {'class': "uofs-subsection"}).get('id')
            split_date_and_day = (re.sub(r'([a-z])([A-Z])', r'\1 \2', date_and_day)).split(" ")
            assert len(split_date_and_day) == 2
            day = split_date_and_day[0]
            date = re.sub('([a-zA-Z]+)([0-9]+)', r'\1-\2', split_date_and_day[1])

            tr_tags = every_day_menu.findAll("tr")
            current_category = ""
            for tr_tag in tr_tags:
                if tr_tag.find("h4"):
                    assert tr_tag.find("h4").getText().lower() in ["lunch", "brunch", "supper"]
                    current_category = tr_tag.find("h4").getText().lower()
                elif tr_tag.find("p"):
                    if current_category != "":
                        current_dish = tr_tag.find("p").getText()
                        my_menu = Menu()
                        my_menu.dish = current_dish
                        my_menu.category = current_category
                        my_menu.date = date
                        my_menu.day = day
                        write_to_tsv(my_menu)


def kick_off_marquis_menu(spider):
    crawler_settings = {
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    }
    process = CrawlerProcess(crawler_settings)
    process.crawl(spider)
    process.start()

kick_off_marquis_menu(MyMenuSpider)

