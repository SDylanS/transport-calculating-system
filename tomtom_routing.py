import requests
import json
import os
from dotenv import load_dotenv
import sys

# Wczytuje zmienne z pliku .env
load_dotenv()
TOMTOM_API_KEY = os.environ.get("TOMTOM_ROUTING_KEY")

# Stała Konfiguracja Pojazdu HGV (Ciężarówka)
# Ustawienia te są używane jako wartości domyślne w funkcji calculate_route.
HGV_DEFAULTS = {
    "vehicleWidth": "2.55",
    "vehicleHeight": "4.0",
    "vehicleLength": "16.5",
    "vehicleNumberOfAxles": "5",
    "vehicleCommercial": "true",
    "travelMode": "truck",
    "report": "effectiveSettings",
}

def calculate_route(origin_coords, destination_coords, total_weight_kg, api_key):
    """
    Oblicza długość trasy, czas i opłaty drogowe z uwzględnieniem parametrów ciężarówki TomTom.

    :param origin_coords: Krotka (lat, lon) punktu początkowego.
    :param destination_coords: Krotka (lat, lon) punktu końcowego.
    :param total_weight_kg: Całkowita waga pojazdu w kg.
    :param api_key: Klucz API TomTom.
    :return: Słownik z wynikami trasy lub None w przypadku błędu.
    """
    if not api_key:
        print("Błąd: Brak klucza API TomTom. Sprawdź plik .env.")
        return None

    BASE_URL = "https://api.tomtom.com/routing/1/calculateRoute/"

    # Budowa parametrów zapytania
    params = {
        "key": api_key,
        "routeType": "fastest",
        "traffic": "true",
        "avoid": "unpavedRoads",
        "routeRepresentation": "summaryOnly",
        "vehicleWeight": str(total_weight_kg)
    }
    
    # Dodanie stałych parametrów HGV
    params.update(HGV_DEFAULTS)

    # Formatowanie współrzędnych i budowa pełnej ścieżki
    route_coords = f"{origin_coords[0]},{origin_coords[1]}:{destination_coords[0]},{destination_coords[1]}"
    full_path_url = BASE_URL + route_coords + "/json"

    print(f"\n--- Rozpoczynam routing HGV dla wagi: {total_weight_kg} kg ---")

    try:
        response = requests.get(full_path_url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Otrzymany status HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print("Szczegóły błędu API TomTom:")
                print(json.dumps(error_data, indent=2))
            except json.JSONDecodeError:
                print(f"Błąd: API nie zwróciło JSON. Odpowiedź tekstowa (max 200 znaków): {response.text[:200]}...")
            return None

        data = response.json()

        if data.get("routes"):
            route = data["routes"][0]
            summary = route["summary"]

            # Ekstrakcja danych trasy
            distance_km = round(summary.get("lengthInMeters", 0) / 1000, 2)
            time_min = round(summary.get("travelTimeInSeconds", 0) / 60)

            # Ekstrakcja opłat drogowych
            tolls_info = route.get("guidance", {}).get("tollVignetteInfo", {}).get("costs", [{}])
            total_tolls = tolls_info[0].get("totalCost", 0) if tolls_info and tolls_info[0].get("totalCost") is not None else 0
            tolls_currency = tolls_info[0].get("currency", "N/A") if tolls_info else "N/A"

            print(f"\nWyniki routingu HGV (TomTom):")
            print(f"  Odległość: {distance_km} km")
            print(f"  Szacowany czas jazdy: {time_min} minut")
            print(f"  Opłaty drogowe: {total_tolls} {tolls_currency}")
            print("-" * 35)

            return {
                "distance_km": distance_km,
                "time_min": time_min,
                "tolls": total_tolls,
                "currency": tolls_currency
            }

        print("Błąd: TomTom API zwróciło pustą odpowiedź (brak trasy).")
        return None

    except requests.exceptions.RequestException as e:
        print(f"\nBłąd Komunikacji z API TomTom: {e}")
        return None
    except Exception as e:
        print(f"\nNieoczekiwany błąd podczas przetwarzania: {e}")
        return None

# Blok testowy
if __name__ == '__main__':
    print("Uruchomiono moduł TomTom HGV Router...")

    try:
        TEST_TOTAL_WEIGHT_KG = int(os.environ.get("TEST_TOTAL_WEIGHT_KG", 38500))
        # Używamy zmiennych pomocniczych dla czytelności konwersji
        lat_origin = os.environ.get("TEST_ORIGIN_LAT")
        lon_origin = os.environ.get("TEST_ORIGIN_LON")
        lat_dest = os.environ.get("TEST_DESTINATION_LAT")
        lon_dest = os.environ.get("TEST_DESTINATION_LON")

        # Sprawdzamy, czy wszystkie zmienne są obecne przed konwersją
        if not all([lat_origin, lon_origin, lat_dest, lon_dest]):
             raise ValueError("Brak jednej ze zmiennych LAT/LON w .env")

        TEST_ORIGIN = (float(lat_origin), float(lon_origin))
        TEST_DESTINATION = (float(lat_dest), float(lon_dest))

        print(f"Wczytano dane testowe: {TEST_ORIGIN} -> {TEST_DESTINATION} | Waga: {TEST_TOTAL_WEIGHT_KG} kg")

    except (TypeError, ValueError) as e:
        print(f"Błąd: Upewnij się, że zmienne testowe w pliku .env są ustawione poprawnie jako liczby. Szczegóły: {e}")
        sys.exit(1)

    print("-" * 35)

    if TOMTOM_API_KEY:
        calculate_route(
            TEST_ORIGIN,
            TEST_DESTINATION,
            TEST_TOTAL_WEIGHT_KG,
            TOMTOM_API_KEY
        )
    else:
        print("Błąd uruchomienia: Proszę ustawić zmienną **TOMTOM_ROUTING_KEY** w pliku **.env**.")