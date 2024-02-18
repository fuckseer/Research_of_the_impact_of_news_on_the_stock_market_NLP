import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
import feedparser

from selenium import webdriver
from selenium.common import MoveTargetOutOfBoundsException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By


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


def configure_driver():
    """Configures and returns a headless Chrome WebDriver."""
    driver_options = webdriver.ChromeOptions()
    driver_options.headless = True
    return webdriver.Chrome(options=driver_options)


def scrape_article_content(url):
    """Scrapes and returns the content of a news article."""
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    paragraphs = soup.find_all("p")
    full_text = " ".join(p.get_text() for p in paragraphs)
    publication_date = soup.find("time")["datetime"]
    return full_text, publication_date


def scrape_news_article(driver, current_index):
    """Scrapes a single news article."""
    title_element = driver.find_element(By.XPATH,
                                        f'//*[@id="__next"]/div[2]/div[2]/div[2]/div[1]/div[2]/ul/li[{current_index}]/article/div/a')
    title = title_element.text

    driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});",
                          title_element)
    time.sleep(0.3)

    author = driver.find_element(By.XPATH,
                                 f'//*[@id="__next"]/div[2]/div[2]/div[2]/div[1]/div[2]/ul/li[{current_index}]/article/div/ul/li[1]/span[2]').text

    if author != 'Investing.com':
        title_element.click()
        time.sleep(0.3)
        read_more_link = driver.find_element(By.PARTIAL_LINK_TEXT, 'Читать далее')
        url = read_more_link.get_attribute('href')
        full_text, publication_date = scrape_article_content(url)
        actions = ActionChains(driver)
        actions.move_by_offset(10, 100).perform()
        time.sleep(0.3)
        actions.click().perform()

    else:
        title_element.click()
        time.sleep(0.3)
        url = driver.current_url
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        full_text = " ".join(p.text for p in paragraphs)
        publication_date = driver.find_element(By.XPATH, '//*[@id="leftColumn"]/div[3]/span').text
        driver.execute_script("window.history.go(-1)")


    return title, full_text, publication_date, url


def process_stock(stock, page=1, look_back_days=3, start_index=1):
    driver = configure_driver()
    news_df = pd.DataFrame(columns=['Title', 'Date', 'Link', 'Text', 'Stock'])

    try:
        news_url = 'https://ru.investing.com/equities/{}_rts-news/{}'.format(stock.lower(), page)
        driver.get(news_url)
        time.sleep(0.3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.3)

        current_index = start_index
        while True:
            try:
                if current_index > 10:

                    next_button = driver.find_element(By.XPATH,
                                                      '//*[@id="__next"]/div[2]/div[2]/div[2]/div[1]/div[3]/button[2]')
                    driver.execute_script("window.scrollTo(0, 800);")
                    driver.implicitly_wait(0.3)
                    next_button.click()
                    time.sleep(0.3)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    current_index = 1
                    page += 1

                title, full_text, publication_date, url = scrape_news_article(driver, current_index)
                new_row = pd.DataFrame([{'Title': title, 'Date': publication_date, 'Link': url, 'Text': full_text, 'Stock': stock}])
                new_row.to_csv('news_2.csv', mode='a', index=False, header=False)
                news_df = pd.concat([news_df, new_row], ignore_index=True)
                print(news_df, current_index)
                current_index += 1

            except Exception as e:
                print(e)
                driver.quit()
                process_stock(stock, page, look_back_days, current_index+1)

            if len(news_df) >= 5000:
                break

    finally:
        driver.quit()

    return news_df


def scrape_investing_news(stock, stock_2, stock_3, stock_4, stock_5, page=1, look_back_days=3, start_index=1):
    stocks_to_process = [stock, stock_2, stock_3, stock_4, stock_5]

    with ThreadPoolExecutor(max_workers=len(stocks_to_process)) as executor:
        results = executor.map(process_stock, stocks_to_process, [page]*len(stocks_to_process),
                               [look_back_days]*len(stocks_to_process), [start_index]*len(stocks_to_process))

    combined_df = pd.concat(results, ignore_index=True)
    return combined_df


df = scrape_investing_news('gazprom', 'novatek', 'rosneft', 'tatneft', 'lukoil', page=1, look_back_days=3, start_index=1)
df = df.to_csv('news_final.csv')
