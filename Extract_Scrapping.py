import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import logging
logging.getLogger('tensorflow').setLevel(logging.FATAL)

import time
from tqdm import tqdm
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from DB_Connexion import connect_Arrango_db
from datetime import datetime, timezone
import re

# --- Chargement des variables d'environnement ---
load_dotenv()

# --- Configuration du logger ---
log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_datefmt = "%H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=log_datefmt,
    handlers=[
        logging.FileHandler("scraping.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ])

# --- Normalisation du titre ---
def normalize_title(titre):
    titre = titre.lower().strip()
    titre = titre.encode("ascii", "ignore").decode("utf-8")
    titre = re.sub(r"[^\w\-]", "_", titre)
    titre = re.sub(r"[-_]+", "_", titre)
    titre = titre[:254]
    if re.match(r"^\d", titre):
        titre = "k_" + titre
    return titre

# --- Vérification existence article via titre ---
def news_exists_by_key(news_col, key):
    return news_col.has(key)

# --- Scraper les URLs à partir d’un mot-clé ---
def get_urls_from_keyword(mot_cle):
    logging.info(f"Recherche mot-clé : '{mot_cle}'")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()
    service.log_path = os.devnull
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(f"https://www.vie-publique.fr/recherche?search_api_fulltext={mot_cle.replace(' ', '+')}")
    time.sleep(3)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.fr-card")
    articles = []

    for card in cards:
        try:
            tag_div = card.find_element(By.CSS_SELECTOR, "div.fr-card__start.vp-type")
            tag_text = tag_div.text.strip().lower()
            if tag_text != "discours":
                continue

            titre_elem = card.find_element(By.CSS_SELECTOR, "h3.fr-card__title a")
            titre = titre_elem.text.strip()
            url = titre_elem.get_attribute("href")

            articles.append({"titre": titre, "url": url})
        except Exception as e:
            logging.warning(f"Erreur lecture carte : {e}")
            continue

    driver.quit()
    logging.info(f"{len(articles)} discours trouvés pour : {mot_cle}")
    return articles

# --- Scraper le contenu d’un article ---
def scrape_infos_news(url, driver):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Titre requis
        try:
            titre = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.fr-h1"))).text.strip()
        except Exception:
            logging.warning(f"Titre introuvable, on skip : {url}")
            return None

        # Auteur requis
        auteur_elem = driver.find_elements(By.CSS_SELECTOR, "div.vp-discours-details")
        if not auteur_elem:
            logging.warning(f"Auteur non trouvé, on skip : {url}")
            return None
        auteur = auteur_elem[0].text.strip()

        # Contenu requis
        contenu_elem = driver.find_elements(By.CSS_SELECTOR, "div.field--name-field-texte-integral")
        if not contenu_elem:
            logging.warning(f"Contenu non trouvé, on skip : {url}")
            return None
        contenu = contenu_elem[0].text.strip()

    except Exception as e:
        logging.warning(f"Erreur scraping {url} : {e}")
        return None

    return {
        "titre": titre,
        "url": url,
        "auteur": auteur,
        "contenu": contenu,
        "date_scraping": datetime.now(timezone.utc).isoformat()
    }


# --- Fonction principale ---
def main():
    db_arrango = connect_Arrango_db()
    news_col = db_arrango.collection("news")

    recherches = [
        ("code de la défense", "CODE_DEFENSE"),
        ("code de la fonction publique", "CODE_FONCTION_PUBLIQUE")
    ]

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()
    service.log_path = os.devnull
    driver = webdriver.Chrome(service=service, options=options)

    for mot_cle, racine in recherches:
        urls = get_urls_from_keyword(mot_cle)

        for entry in urls:
            url = entry["url"]
            logging.info(f"Scraping de l'article : {url}")

            infos = scrape_infos_news(url, driver)
            if infos is None:
                continue
            infos["code"] = racine

            key = normalize_title(infos["titre"])
            infos["_key"] = key

            try:
                if not news_exists_by_key(news_col, key):
                    news_col.insert(infos)
                    logging.info(f"Article inséré : {infos['titre']}")
                else:
                    logging.info(f"Article déjà présent : {infos['titre']}")
            except Exception as e:
                logging.error(f"Erreur d'insertion dans ArangoDB : {e}")

    driver.quit()
    logging.info("Scraping terminé pour tous les codes.")

# --- Lancement ---
if __name__ == "__main__":
    main()
