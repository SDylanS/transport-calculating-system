import time
import json
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

# ==============================================================================
# KONFIGURACJA LOGOWANIA
# ==============================================================================
load_dotenv()
LOGIN = os.getenv("DS_LOGIN")
HASLO = os.getenv("DS_HASLO")
if not LOGIN or not HASLO:
    raise ValueError("Błąd: Brak danych w pliku .env!")
# ==============================================================================

def uruchom_snifera():
    print(f"[SNIFFER] Uruchamiam Chrome w trybie podsłuchu sieci...")
    
    # 1. Konfiguracja podsłuchu
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    #Logowanie sieci WebSocket
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # --- LOGOWANIE ---
        print("Wejście na stronę")
        driver.get("https://dslocate.datasystem.pl")
        
        wait = WebDriverWait(driver, 20)
        
        try:
            user_input = wait.until(EC.element_to_be_clickable((By.NAME, "login")))
            pass_input = driver.find_element(By.NAME, "password")
            
            user_input.click()
            user_input.clear()
            user_input.send_keys(LOGIN)
            pass_input.click()
            pass_input.clear()
            pass_input.send_keys(HASLO)
            
            try:
                driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            except:
                pass_input.submit()
                
            print("Zalogowano, oczekiwanie na dalsze połączenie...")
            
        except Exception as e:
            print(f"Błąd logowania: {e}")
            driver.save_screenshot("blad_logowania.png")
            return

        time.sleep(15) 
        print("Nasłuchiwanie pakietów WebSocket (Ctrl+C żeby przerwać)...")
        print("-" * 50)

        # --- GŁÓWNA PĘTLA PODSŁUCHU ---
        while True:
            logs = driver.get_log("performance")
            
            for entry in logs:
                message = json.loads(entry["message"])["message"]
                
                if message["method"] == "Network.webSocketFrameReceived":
                    try:
                        payload = message["params"]["response"]["payloadData"]
                        
                        if "fuel" in payload:
                            if "\n\n" in payload:
                                json_str = payload.split("\n\n")[-1].replace('\x00', '')
                            else:
                                json_str = payload

                            try:
                                dane = json.loads(json_str)
                                pojazdy = dane.get('vehicles', [])
                                
                                for auto in pojazdy:
                                    vid = auto.get('vehicle_id')
                                    paliwo = auto.get('fuel')
                                    lat = auto.get('latitude')
                                    lon = auto.get('longitude')
                                    
                                    print("\n" + "-"*20)
                                    print(f"DANE POJAZDU")
                                    print(f"ID:     {vid}")
                                    print(f"PALIWO: {paliwo} L")
                                    print(f"GPS:    {lat}, {lon}")
                                    print("-"*20)
                                    
                            except:
                                pass
                                
                    except KeyError:
                        pass

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nZatrzymano przez użytkownika.")
    except Exception as e:
        print(f"Błąd krytyczny: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    uruchom_snifera()