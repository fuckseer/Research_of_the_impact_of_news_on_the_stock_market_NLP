import csv
import requests
from bs4 import BeautifulSoup
import feedparser


def save_data(article_list):
    with open('articles.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=article_list[0])
        writer.writeheader()
        writer.writerows(article_list)


def scrap_text(name, link):
    r = requests.get(link)
    soup = BeautifulSoup(r.text, features='lxml')

    if name == 'Investing':
        div = soup.find('div', class_='WYSIWYG articlePage')
        paragraphs = div.find_all('p')
        article_text = ""

        for paragraph in paragraphs:
            article_text += paragraph.text

        index_start = article_text.find('\n')
        index_finish = article_text.find("Читайте оригинальную статью")
        print(article_text)
        return article_text[index_start + 1:index_finish]

    elif name == 'Finam':
        print(soup.text)
        div = soup.find('div', class_='clearfix mb2x')
        paragraphs = div.find_all('p')
        article_text = ""

        for paragraph in paragraphs:
            article_text += paragraph.text

        return article_text

    elif name == 'Газпром':
        div = soup.find('div', {'class': 'text-block'})
        paragraphs = div.find_all('p')
        article_text = ""

        for paragraph in paragraphs:
            article_text += paragraph.text

        return article_text

    elif name == 'Роснефть':
        div = soup.find('div', {'class': 'common-text'})
        paragraphs = div.find_all('p')
        article_text = ""

        for paragraph in paragraphs:
            article_text += paragraph.text

        return article_text

    elif name == 'Лукойл':
        div = soup.find('div', {'class': 'content'})
        paragraphs = div.find_all('p')
        article_text = ""

        for paragraph in paragraphs:
            article_text += paragraph.text

        return article_text


def scrap_rss(name, url):
    article_list = []

    try:
        feed = feedparser.parse(url)
        #print(feed.items())
        for a in feed['items']:
            title = a.title
            link = a.link
            print(link)
            published = a.published
            text = scrap_text(name, link)
            article = {
                'title': title,
                'link': link,
                'published': published,
                'text': text.replace('\xa0', ' ')
            }
            article_list.append(article)
            print(article_list)
        return save_data(article_list)
    except Exception as e:
        print('The scraping is failed. Exception:')
        print(e)


scrap_rss('Finam',
          'https://www.finam.ru/analysis/conews/rsspoint/')
