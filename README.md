
# Transport Calculating System 🚛

A Python-based automated tool designed to calculate the profitability of freight transport in real-time. The application integrates with the **Data System** telematics platform to retrieve live vehicle data (GPS location, CAN bus fuel levels) and computes the estimated net profit for a potential shipment based on current operating costs.

## 🚀 Key Features

* **Live Telemetry Extraction:** Retrieves real-time vehicle data (Location, Fuel Level) directly from the Data System web platform.
* **Advanced Automation:** Uses **Selenium WebDriver** in headless mode to handle authentication and navigate the telematics dashboard securely.
* **Network Sniffing:** Bypasses complex API restrictions (STOMP/WebSocket auth) by intercepting browser network traffic (DevTools Protocol) to capture live data streams.
* **Profitability Calculator:** Automatically calculates the estimated profit margin based on:
    * Distance to pickup + Delivery distance.
    * Real-time fuel levels (alerts if refueling is needed).
    * Average fuel consumption, driver costs, and amortization.
* **Secure:** Sensitive credentials are managed via environment variables (`.env`), keeping the source code clean and safe.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Automation:** Selenium WebDriver, Chrome (Headless)
* **Data Processing:** JSON, WebSocket frame parsing
* **Environment:** `python-dotenv`, `webdriver-manager`

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/SDylanS/transport-calculating-system.git](https://github.com/SDylanS/transport-calculating-system.git)
    cd transport-calculating-system
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your Data System credentials:
    ```env
    DS_LOGIN=your_username
    DS_HASLO=your_password
    ```

## ▶️ Usage

Run the main application script:

```bash
python3 app.py
```
<p align="center">
  <video src="code.mp4" loop autoplay style="max-width: 100%;"></video>
</p>
