from google.colab import drive
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd

# Mount Google Drive
drive.mount('/content/drive')

def fetch_news(keyword, url, news_data, max_articles=100):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('a', class_='JtKRv')[:max_articles]
        times = soup.find_all('time', class_='hvbAAd')[:max_articles]
        publishers = soup.find_all('div', class_='vr1PYe')[:max_articles]

        if not articles:
            print("No news found for keyword:", keyword)
            return

        for article, time, publisher in zip(articles, times if times else [None]*len(articles), publishers if publishers else [None]*len(articles)):
            title = article.get_text(strip=True)
            link = 'https://news.google.com' + article['href'][1:]
            utc_time = datetime.strptime(time['datetime'], '%Y-%m-%dT%H:%M:%SZ') if time else datetime.now()
            kst_time = utc_time + timedelta(hours=9)
            formatted_time = kst_time.strftime('%Y-%m-%d')
            publisher_name = publisher.get_text(strip=True) if publisher else 'Unknown Publisher'

            news_data.append([keyword, title, publisher_name, link, formatted_time])
            print(f"Keyword: {keyword} | Title: {title} | Publisher: {publisher_name} | Link: {link} | Date: {formatted_time}")

    except requests.exceptions.RequestException as e:
           print(f"Error fetching news for keyword {keyword}: {e}")

def save_news_to_excel(news_data):
    execution_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    df = pd.DataFrame(news_data, columns=['Keyword', 'Title', 'Publisher', 'Link', 'Posted At'])
    excel_path = f'/content/drive/My Drive/news_feed_{execution_time}.xlsx'
    df.to_excel(excel_path, index=False)
    print(f"Excel file saved to {excel_path}")

if __name__ == "__main__":
    news_data = []
    keywords = []
    while True:
        keyword = input("Enter a keyword for news search (type 'end' to execute): ")
        if keyword.lower() == 'end':
            break
        keywords.append(keyword)

    base_url = 'https://news.google.com/search?q=%22{}%22%20when%3A7d&hl=ko&gl=KR&ceid=KR%3Ako'
    for keyword in keywords:
        url = base_url.format(keyword)
        fetch_news(keyword, url, news_data)

    save_news_to_excel(news_data)
