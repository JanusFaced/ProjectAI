from pathlib import Path
import sys
import os
import requests
from logger_setup import get_logger

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

logger = get_logger(__name__)

OLLAMA_HOST = "http://ollama:11434" 

def ask_ollama(prompt: str, model: str ="llama3.2") -> str:
	payload = {
		"model": model,
		"prompt": prompt,
		"stream": False  # Ставим False, чтобы получить сразу полный ответ
	}
	try:
		response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload)
		response.raise_for_status()
		return response.json()["response"]
	except Exception as e:
		return f"Ошибка: {e}"

def main() -> None:

	list_of_models: Dict = {
		"S": "gemma3:1b-it-q4_K_M",
		"M": "gemma3:4b-it-q4_K_M",
		"L": "gemma3:12b-it-q4_K_M",
		"XL": "gemma3:27b-it-q4_K_M",

	}

	messege: str = """
	Напиши "Привет" на нескольких языках мира.
	"""

	answer: str = ask_ollama(prompt=messege, model=list_of_models["S"])
	logger.info(answer)

main()