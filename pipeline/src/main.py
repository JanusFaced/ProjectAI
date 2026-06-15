from pathlib import Path
import sys
import os
import requests
import feedparser
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from logger_setup import get_logger

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

logger = get_logger(__name__)

OLLAMA_HOST = "http://ollama:11434"

def main() -> None:
	list_of_messeges: list = fetch_news_from_rss()

	for messege in list_of_messeges:
		logger.info(messege)
		answer: str = ai_model(prompt=messege)
		logger.info(answer)

def clean_html(text: str) -> str:
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()

def fetch_news_from_rss(feed_url: str = "BBC", hours_back: int = 24) -> list:

	list_rss_feeds: dict = {
		"BBC": "http://feeds.bbci.co.uk/news/rss.xml",
		"Reuters": "https://www.reuters.com/news/rss/topNews",
		"TechCrunch": "http://feeds.feedburner.com/TechCrunch",
		"Habr": "https://habr.com/ru/rss/all/all/?fl=ru"
	}

	list_of_messeges: list = []

	for name, feed_url in list_rss_feeds.items():
		logger.info(name)
		
		feed = feedparser.parse(feed_url)
		cutoff = datetime.now() - timedelta(hours=hours_back)

		articles: list = []
		for entry in feed.entries:
			pub_date = datetime(*entry.published_parsed[:6])
			if pub_date > cutoff:
				articles.append({
					"title": entry.title,
					"link": entry.link,
					"published": pub_date,
					"summary": entry.get("summary", "")[:500]
				})
		
		articles = [x['summary'] for x in articles]
		article = '.'.join(articles)
		article = clean_html(article)
		list_of_messeges.append(article)


	return list_of_messeges


def ai_model(prompt: str) -> str:

	list_of_models: Dict = {
		"S": "gemma3:1b-it-q4_K_M",
		"M": "gemma3:4b-it-q4_K_M",
		"L": "gemma3:12b-it-q4_K_M",
		"XL": "gemma3:27b-it-q4_K_M",

	}

	system = """
	Ты — агрегатор новостей. Твоя задача: пересказывать новости максимально кратко.

	ЖЁСТКИЕ ПРАВИЛА:
	1. Ответ должен быть ОДНИМ абзацем из 2-4 предложений
	2. НИКАКИХ списков, нумерации, заголовков, разделов
	3. НИКАКИХ оценок, выводов, аналитики — только факты
	4. НИКАКИХ фраз типа "вот пересказ", "текст говорит о том, что"
	5. Просто напиши, ЧТО случилось: КТО, ГДЕ, КОГДА, ЧТО сделал
	6. Ответ давай только на русском, даже если статья на английском

	"""

	payload = {
		"model": list_of_models["S"],
		"prompt": prompt,
		"system": system,
		"stream": False,
		"keep_alive": "5m",
		"options": {
			"num_ctx": 4096,
			"num_predict": 1024,
			"temperature": 0.2,
			"top_p": 0.50,
			"top_k": 20,
			"repeat_penalty": 1.1,
			"repeat_last_n": 64
		}
	}

	try:
		response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload)
		response.raise_for_status()
		return response.json()["response"]
	
	except Exception as e:
		return f"Ошибка: {e}"

main()