import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser

from selenium import webdriver


def save_data(article_list):
    pd.DataFrame(article_list).to_csv('articles.csv', mode='a')


def scrap_text(name, link):
    try:
        if name == 'Investing':
            r = requests.get(link)
            soup = BeautifulSoup(r.content, features='lxml')
            div = soup.find('div', class_='WYSIWYG articlePage')
            article_text = join_paragraphs(div)
            index_start = article_text.find('\n')
            index_finish = article_text.find("Читайте оригинальную статью")

            return article_text[index_start + 1:index_finish]

        elif name == 'Finam':
            driver = webdriver.Chrome()
            driver.get(link)
            source_data = driver.page_source
            soup = BeautifulSoup(source_data, features='lxml')
            div = soup.find('div', class_='clearfix mb2x')
            article_text = join_paragraphs(div)

            return article_text

        elif name == 'Газпром':
            r = requests.get(link)
            soup = BeautifulSoup(r.content, features='lxml')
            div = soup.find('div', class_='text-block')
            article_text = join_paragraphs(div)

            return article_text
        elif name == 'Лукойл':
            r = requests.get(link)
            soup = BeautifulSoup(r.content, features='lxml')
            div = soup.find('div', class_='content')
            article_text = join_paragraphs(div)

            return article_text

        else:
            raise ValueError('Некорректное имя источника')
    except ValueError as e:
        print(e)
        return None
    except requests.exceptions.RequestException:
        print('Ошибка при запросе страницы')
        return None
    except AttributeError:
        print('Элементы не найдены на странице')
        return None


def join_paragraphs(div):
    paragraphs = div.find_all('p')
    article_text = ""
    for paragraph in paragraphs:
        article_text += paragraph.text
    return article_text


def scrap_rss(name, url):
    article_list = []
    if name == 'Роснефть':
        return save_data(scrap_rss_rosneft(url))

    try:
        feed = feedparser.parse(url)
        for a in feed['items']:
            title = a.title
            link = a.link
            published = a.published
            text = scrap_text(name, link)
            article = {
                'title': title,
                'link': link,
                'published': published,
                'text': text
            }
            print(article)
            article_list.append(article)
        return save_data(article_list)
    except Exception as e:
        print('The scraping is failed. Exception:')
        print(e)


def scrap_rss_rosneft(url):
    driver = webdriver.Chrome()
    driver.get(url)
    source_data = driver.page_source
    soup = BeautifulSoup(source_data, features='lxml')
    article_list = []
    for item in soup.find_all('item'):
        title = item.title.text
        link = item.find('link').next_sibling.strip()
        pub_date = item.pubdate.text
        article_text = ''
        description = item.find_all('yandex:full-text')
        for paragraph in description:
            article_text += paragraph.get_text()

        article_text = re.sub('<.*?>|&.*?;', '', article_text)
        article = {
            'title': title,
            'link': link,
            'published': pub_date,
            'text': article_text
        }
        print(article)
        article_list.append(article)

        return article_list


scrap_rss('Finam', 'https://www.finam.ru/analysis/conews/rsspoint/')