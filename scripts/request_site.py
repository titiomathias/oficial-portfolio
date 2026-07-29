import cloudscraper
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import dotenv_values

config = dotenv_values(".env")

FILE_PATH = Path(__file__).parent / "feedbacks.json"


def base_url():
    base = config.get("URL") or os.getenv("URL")
    if not base:
        raise RuntimeError("variável URL não configurada (.env ou ambiente)")
    return base.rstrip("/")


def request_site():
    base = base_url()
    scraper = cloudscraper.create_scraper()
    response = scraper.get(f"{base}/user/tio-mathias")

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        feedbacks = []

        for item in soup.find_all("li", class_='box-loader-item'):
            left_elements = item.find_all(class_="project-info-left")
            right_elements = item.find_all(class_="project-info-right")

            for p, x in zip(left_elements, right_elements):
                data = {}
                if "Cancelado" not in x.get_text():
                    data["link"] = f"{base}{p.a.get('href')}"
                    data["title"] = p.a.get_text().strip()
                    data["comment"] = p.find(class_="project-comment").get_text().strip()
                    feedbacks.append(data)

        with open(FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(feedbacks, file, ensure_ascii=False, indent=4)

        return feedbacks
    else:
        return {"error": "fail to access site"}
    

def get_feedbacks():
    if not os.path.exists(FILE_PATH):
        return request_site()

    last_modified = datetime.fromtimestamp(os.path.getmtime(FILE_PATH))
    now = datetime.now()

    if now - last_modified < timedelta(days=1):
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return request_site()