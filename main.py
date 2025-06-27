import random
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

playlists = [
    "https://www.youtube.com/watch?v=eglj6ecrjNo&list=PLd3AxEHWurtIM9aLs4NSOfb8Sj1hiommb",
    "https://www.youtube.com/watch?v=X0_cBVoH3-Q&list=PLd3AxEHWurtKvLI_j4eIiWWz2N-JM-NHB",
    "https://www.youtube.com/watch?v=S8BOtrZ65aY&list=PLd3AxEHWurtLS_YGklIJorgvaPXk5qNW6"
]

def get_random_playlist():
    return random.choice(playlists)

def click_cookie_popup(driver):
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((
            By.XPATH,
            '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog'
        )))
        print("Cookie-popup hittades.")

        accept_button = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/yt-button-shape/button'
        )))
        accept_button.click()
        print("Cookie-popup klickades bort.")
        time.sleep(1)
    except Exception as e:
        print("Cookie-popup visades inte eller kunde inte klickas bort:", e)

def keep_video_alive(driver):
    actions = ActionChains(driver)

    driver.execute_script("window.focus();")

    try:
        # Scrolla lite upp och ner för att visa aktivitet
        driver.execute_script("window.scrollBy(0, 100);")
        time.sleep(0.5)
        driver.execute_script("window.scrollBy(0, -100);")
        time.sleep(0.5)

        # Skicka högerpil för att byta till nästa video (utan paus)
        actions.send_keys(Keys.ARROW_RIGHT).perform()

        print("Skickade högerpil för att hålla videon levande.")
    except Exception as e:
        print("Misslyckades hålla videon aktiv:", e)

def play_playlist_with_selenium(playlist):
    if not playlist or not playlist.startswith("https:"):
        print("Ogiltig eller tom spellista.")
        return

    print(f"Spelar spellista: {playlist}")

    options = Options()
    options.add_argument("--headless=new")  # Kommentera ut för att se vad som händer
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--mute-audio")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")

    driver_path = os.path.join(os.path.dirname(__file__), "chromedriver", "chromedriver.exe")
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(playlist)
        print("YouTube-spellista öppnad.")

        click_cookie_popup(driver)

        wait = WebDriverWait(driver, 15)

        # Vänta på att första videon laddar (klicka inte om video startar automatiskt)
        time.sleep(5)

        # Klicka på shuffle om du vill ha det levande
        try:
            shuffle_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-shuffle-button")))
            shuffle_button.click()
            print("Shuffle-knappen klickades.")
        except Exception as e:
            print("Shuffle-knappen hittades inte eller kunde inte klickas:", e)

        # Kör en loop i 60 minuter, håll videon levande, refresha var 30:e sekund
        start_time = time.time()
        while time.time() - start_time < 3600:
            keep_video_alive(driver)
            time.sleep(25)
            driver.refresh()
            print("Sidan refreshad för att undvika crash.")

    except Exception as e:
        print("Fel uppstod:", e)

    finally:
        driver.quit()
        print("Webbläsaren stängdes efter 1 timme.")

def main():
    try:
        for i in range(3):  # Exempel på 3 spellistor
            playlist = get_random_playlist()
            play_playlist_with_selenium(playlist)
    except Exception as e:
        print("Ett allvarligt fel inträffade i huvudflödet:", e)

if __name__ == "__main__":
    main()
