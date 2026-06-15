from pathlib import Path
import sys
import os
import requests
from logger_setup import get_logger

current_file_path = Path(__file__).resolve()
current_dir = current_file_path.parent

logger = get_logger(__name__)

OLLAMA_HOST = "http://ollama:11434"

def ai_model(prompt: str) -> str:

	list_of_models: Dict = {
		"S": "gemma3:1b-it-q4_K_M",
		"M": "gemma3:4b-it-q4_K_M",
		"L": "gemma3:12b-it-q4_K_M",
		"XL": "gemma3:27b-it-q4_K_M",

	}

	system = "Ты — креативный разработчик с богатым воображением."

	payload={
		"model": list_of_models["S"],
		"prompt": prompt,
		"system": system,
		"stream": False,
		"keep_alive": "5m",
		"options": {
			"num_ctx": 4096,
			"num_predict": 4096,
			"temperature": 0.9,
			"top_p": 0.95,
			"top_k": 60,
			"repeat_penalty": 1.15,
			"repeat_last_n": 64
		}
	}

	try:
		response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload)
		response.raise_for_status()
		return response.json()["response"]
	
	except Exception as e:
		return f"Ошибка: {e}"

def main() -> None:

	messege: str = """
	Дай несколько бизнес идей с ИИ.
	"""

	answer: str = ai_model(prompt=messege)
	logger.info(answer)

main()