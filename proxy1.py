import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from bs4 import BeautifulSoup
import re
import time
import random
import os
import requests


def is_proxy_valid(proxy):
    try:
        response = requests.get('http://www.google.com', proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            print(f"Geçerli proxy: {proxy}")
            return True
        else:
            print(f"Geçersiz proxy (Yanıt kodu {response.status_code}): {proxy}")
            return False
    except requests.RequestException as e:
        print(f"Proxy test hatası ({proxy}): {e}")
        return False


def load_proxies(proxy_list):
    # Proxy listeden rastgele seç
    while proxy_list:
        proxy = random.choice(proxy_list)
        if is_proxy_valid(proxy):
            print(f"Geçerli proxy bulundu: {proxy}")
            return proxy  # Geçerli proxy'yi döndür
        else:
            print(f"Geçersiz proxy: {proxy}, başka bir tane deneniyor...")
            proxy_list.remove(proxy)
    print("Geçerli bir proxy bulunamadı.")
    return None
def create_driver_with_proxy(valid_proxy):
    chrome_options = Options()
    chrome_options.add_argument(f'--proxy-server={valid_proxy}')
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')

    service = Service('C:\\Users\\Gülay\\Desktop\\chromedriver\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


proxy_list = [
    "94.103.92.163:3128",
    "5.17.6.83:8080",
    "43.132.219.102:80",
    "123.126.158.50:80",
]


valid_proxy = load_proxies(proxy_list)
driver = create_driver_with_proxy(valid_proxy) if valid_proxy else None

if not driver:
    print("Geçerli bir proxy bulunamadı.")
    exit()

def load_processed_batches(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return {int(line.strip()) for line in f}
    else:
        return set()


def save_processed_batch(file_name, batch_index):
    with open(file_name, 'a') as f:  # 'a' moduyla ekleme
        f.write(f"{batch_index}\n")


def clean_phone_number(phone_number):
    return re.sub(r'\D', '', phone_number)


def clean_email(email):
    return email.strip()


def is_ad(driver, element):
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of(element))
        ad_labels = element.find_elements(By.CSS_SELECTOR, ".ad-icon")
        if ad_labels:
            return True
        url = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        if any(ad_site in url for ad_site in ["googleadservices.com", "google.com/ads"]):
            return True
        if "ad" in url.lower():
            return True
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        return False
    return False


def find_contact_page_link(driver):
    contact_keywords = ["contact", "about", "contact us", "communication", "get in touch", "reach us", "support", "help", "about us",
                        "contactez nous", "kontakt", "联系", "联系我们", "联系方式", "支持", "帮助"]
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        try:
            link_text = link.text.strip().lower()
            if any(keyword in link_text for keyword in contact_keywords):
                return link
        except StaleElementReferenceException:
            continue
    return None

def find_contact_info(soup):
    phone_numbers = []
    phone_regex = re.compile(r"[+()]?[1-9][0-9 .()-]{8,}[0-9]")
    for text in soup.stripped_strings:
        phone_numbers.extend(phone_regex.findall(text))

    email_addresses = []
    email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    for text in soup.stripped_strings:
        email_addresses.extend(email_regex.findall(text))

    return phone_numbers, email_addresses

def scrape_google_results(search_query, driver):
    print(f"Arama yapılıyor: {search_query}")
    driver.get(f"https://www.google.com/search?q={search_query}")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tF2Cxc")))
    except TimeoutException:
        print("Arama sonuçları yüklenemedi.")
        return None, None, [], []

    search_results = driver.find_elements(By.CSS_SELECTOR, ".tF2Cxc")
    organic_results = [result for result in search_results if not is_ad(driver, result)]

    # Valid website kontrolü
    valid_websites = [
        "facebook.com", "instagram.com", "twitter.com",
        "linkedin.com", "pinterest.com", "youtube.com",
        "amazon.com"
    ]

    if organic_results:
        for result in organic_results:
            attempts = 2  # Stale element hatası için deneme sayısı
            while attempts > 0:
                try:
                    link = result.find_element(By.CSS_SELECTOR, "a")
                    href = link.get_attribute("href")

                    if any(website in href for website in valid_websites):
                        print(f"Geçersiz URL (sosyal medya veya diğer bilinen site): {href}")
                        break

                    print(f"URL ziyaret ediliyor: {href}")
                    link.click()

                    contact_page_link = find_contact_page_link(driver)

                    if contact_page_link:
                        print("İletişim sayfası bulundu ve ziyaret ediliyor.")
                        contact_page_link.click()

                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body")))

                        contact_page_html = driver.page_source
                        soup = BeautifulSoup(contact_page_html, 'html.parser')

                        phone_numbers, email_addresses = find_contact_info(soup)

                        print(f"Telefon numaraları: {phone_numbers}")
                        print(f"E-posta adresleri: {email_addresses}")

                        driver.back()

                        return href, contact_page_link.get_attribute("href"), phone_numbers, email_addresses
                    else:
                        print("İletişim sayfası bağlantısı bulunamadı.")
                        driver.back()
                        return href, None, [], []

                    break

                except StaleElementReferenceException:
                    print("Stale element hatası oluştu. Yeniden deniyor...")
                    attempts -= 1
                    if attempts == 0:
                        print("Bağlantı bulunamadı, bir sonraki şirkete geçiliyor.")
            else:
                continue

    return None, None, [], []

def save_results(results, batch_index):
    file_name = f'batch_{batch_index + 1}.xlsx'
    df = pd.DataFrame(results, columns=["Şirket", "URL", "E-postalar", "Telefonlar"])
    df.to_excel(file_name, index=False)

def main():
    df = pd.read_excel('train.xlsx', header=None)
    batch_size = 5
    batches = [df[i:i + batch_size] for i in range(0, df.shape[0], batch_size)]
    processed_batches = load_processed_batches('processed_batches.txt')
    all_batches_results = []


    for batch_index, batch in enumerate(batches):
        if batch_index in processed_batches:
            print(f"Batch {batch_index + 1} zaten işlendi, atlanıyor.")
            continue

        batch_results = []
        for company_name in batch[0]:
            company_name_clean = company_name.strip().replace(" ", "+")
            search_query = f"{company_name_clean} iletişim sayfası"
            href, contact_page_link, phone_numbers, email_addresses = scrape_google_results(search_query, driver)

            batch_results.append([company_name, href, email_addresses, phone_numbers])

        all_batches_results.extend(batch_results)
        save_processed_batch('processed_batches.txt', batch_index)
        save_results(batch_results, batch_index)

    driver.quit()

if __name__ == "__main__":
    main()
