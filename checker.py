import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# URL der Kabelwerk-Seite mit freien Objekten
URL = "https://www.kabelwerk.at/freie-objekte/kabelwerk/"
HASH_FILE = "last_hash.txt"

# Umgebungsvariablen für E-Mail
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def get_site_content():
    """
    Ruft nur den relevanten Teil der Website ab – den Abschnitt mit freien Objekten.
    """
    resp = requests.get(URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Zielbereich: Liste der freien Objekte
    teaser_list = soup.find("div", class_="c-teaser-list")
    if not teaser_list:
        raise ValueError("⚠️ Abschnitt mit class='c-teaser-list' wurde nicht gefunden.")

    # Optional: Nur Linktexte extrahieren für noch stabileren Vergleich
    items = teaser_list.find_all("a", class_="c-teaser__link")
    return "\n".join(item.get_text(strip=True) for item in items)

def get_hash(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_last_hash():
    if not os.path.exists(HASH_FILE):
        return ""
    with open(HASH_FILE, "r") as f:
        return f.read().strip()

def save_hash(h):
    with open(HASH_FILE, "w") as f:
        f.write(h)

def send_email():
    msg = MIMEText(f"Die Website {URL} hat sich geändert.")
    msg["Subject"] = "🔔 Änderung erkannt – Kabelwerk"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP("mail.gmx.net", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    print("📧 E-Mail gesendet an", EMAIL_RECEIVER)

def main():
    try:
        content = get_site_content()
        current_hash = get_hash(content)
        last_hash = load_last_hash()

        if current_hash != last_hash:
            print("🆕 Änderung erkannt!")
            send_email()
            save_hash(current_hash)
        else:
            print("⏳ Keine Änderung.")
    except Exception as e:
        print(f"❌ Fehler bei der Verarbeitung: {e}")

if __name__ == "__main__":
    main()
