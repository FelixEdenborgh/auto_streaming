import mysql.connector
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

# Läs in miljövariabler från .env-filen
#load_dotenv()

dotenv_path = '/root/.env'
load_dotenv(dotenv_path=dotenv_path)

# Använd miljövariabler för att ansluta till databasen
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


# Anslut till databasen
def connect_db():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )


# Hämta en slumpmässig spellista
def get_random_playlist():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT link FROM playlists ORDER BY RAND() LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None


# Hämta en spellista som börjar med https
def get_playlist_with_https():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT link FROM playlists WHERE link LIKE 'https:%' ORDER BY RAND() LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None

def play_playlist_with_selenium(playlist):
    if not playlist:
        print("Ingen spellista hittades, försöker igen med länkar som börjar på 'https:'")
        playlist = get_playlist_with_https()

    if playlist:
        print(f"Spelar spellista: {playlist}")

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")  # Viktigt för headless
        options.add_argument("--disable-gpu")  # Ibland krävs i vissa miljöer

        driver_path = os.path.join(os.path.dirname(__file__), "chromedriver", "chromedriver")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(playlist)
            print("Spellista öppnad i webbläsaren.")
            wait = WebDriverWait(driver, 20)

            time.sleep(5)  # Låt sidan ladda helt

            # Försök klicka på shuffle-knappen
            try:
                shuffle_button = wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//button[./svg[@width="29" and @height="26"]]'
                )))
                driver.execute_script("arguments[0].click();", shuffle_button)
                print("Shuffle-knappen klickad via JS.")
                time.sleep(1)
            except Exception as shuffle_error:
                print("Kunde inte hitta eller klicka på Shuffle-knappen:", shuffle_error)

            # Försök klicka på play-knappen
            try:
                play_button = wait.until(EC.element_to_be_clickable((
                    By.XPATH, '//button[@aria-label="Play song"]'
                )))
                driver.execute_script("arguments[0].click();", play_button)
                print("Play-knappen klickad via JS.")
            except Exception as play_error:
                print("Kunde inte hitta eller klicka på Play-knappen:", play_error)
                return

            print("Spellistan spelas nu. Väntar i 1 timme (3600 sekunder)...")
            time.sleep(3600)

        except Exception as e:
            print("Fel uppstod:", e)

        finally:
            driver.quit()
            print("Webbläsaren stängdes efter 1 timme.")
    else:
        print("Ingen spellista med 'https:'-länkar hittades.")





# Main-funktion
def main():
    try:
        for _ in range(9):  # Kör 9 gånger
            playlist = get_random_playlist()
            if playlist:
                print(f"Spelar spellista: {playlist}")
                play_playlist_with_selenium(playlist)
            else:
                print("Ingen spellista hittades. Försöker igen med 'https:'-länkar.")
                play_playlist_with_selenium(None)
    except Exception as e:
        print("Ett allvarligt fel inträffade i huvudflödet:", e)



if __name__ == "__main__":
    main()
