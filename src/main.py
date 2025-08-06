import json
import time
from dataclasses import dataclass,asdict
from pathlib import Path
from pprint import pprint
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

def get_url_html(url:str):
    res = requests.get(
        url,
        headers={
            'User-Agent':UserAgent().random
        }
    )
    return res.text

def get_soup(html_text : str) -> BeautifulSoup:
    return BeautifulSoup(html_text, 'lxml')

@dataclass
class ArticleData:
    title: str
    views: str
    link: str
    text: dict

def get_post_text(url:str):
    print(f"Получаю контент {url=}")
    time.sleep(1)
    soup = get_soup(get_url_html(url))
    all_articles_soup = soup.find('div',class_='article-formatted-body')

    paragraphs = [p.get_text(strip=True) for p in all_articles_soup.find_all('p') if p.get_text(strip=True)]

    text = {
        "article_content": paragraphs,
    }
    print(f"Успешно получил контент {url=}")
    return text


def get_all_habr_posts(soup : BeautifulSoup)->list[ArticleData]:
    posts_data = []
    all_articles_soup = soup.find_all("article",class_="tm-articles-list__item")
    for article in all_articles_soup:
        article_title :str = article.find("a",class_="tm-title__link").find("span").text
        article_url: str = "https://habr.com" + article.find("h2",class_="tm-title tm-title_h2").find("a")["href"]
        article_views : str= article.find("span", class_="tm-icon-counter__value").text

        print(f"Обрабатываю страницу {article_url=}")
        post_text = get_post_text(article_url)

        DATA_DIR = Path(__file__).parent.parent / 'data'
        file_name = f'{article_url.split('/')[-2]}.json'
        file_path = DATA_DIR / file_name

        article_data = ArticleData(
            title=article_title,
            views=article_views,
            text= post_text,
            link = article_url,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(asdict(article_data), f, ensure_ascii=False, indent=2)

        posts_data.append(article_data)
        print(f"Добавил страницу в файл {article_url=}\n")
        time.sleep(1)

    return posts_data


def main():
    main_page = 'https://habr.com/ru/articles/top/daily/'
    html = get_url_html(main_page)
    soup = get_soup(html)
    posts = get_all_habr_posts(soup)
    pprint(posts)

if __name__ == '__main__':
    main()