import requests
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from scrape_practitioner_details import get_practitioner_details
url = "https://vicopendatavba.blob.core.windows.net/vicopendata/BPR.csv"
out_path = "BPR.csv"

# with requests.get(url, stream=True) as r:
#     r.raise_for_status()
#     with open(out_path, "wb") as f:
#         for chunk in r.iter_content(chunk_size=8192):
#             if chunk:
#                 f.write(chunk)

# print(f"Saved to {out_path}")

df = pd.read_csv(out_path)
print(df['Accreditation ID'].head(5))

ids = []
with open("BPR.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ids.append(row["Accreditation ID"])
        if len(ids) == 3:
            break

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.get("https://bams.vba.vic.gov.au/bams/s/practitioner-search")  # example URL
wait = WebDriverWait(driver, 5)
reg_input = driver.execute_script("""
function findInput(root) {
    if (!root) return null;

    const input = root.querySelector('input[name="registrationNumber"]');
    if (input) return input;

    const elements = root.querySelectorAll('*');
    for (const el of elements) {
        if (el.shadowRoot) {
            const found = findInput(el.shadowRoot);
            if (found) return found;
        }
    }
    return null;
}
return findInput(document);
""")

if not reg_input:
    raise Exception("Registration input not found")


i=5
while (i<10):

    reg_input.click()
    reg_input.clear()
    print(f"Searching for {df.loc[i,"Accreditation ID"]}")
    reg_input.send_keys(df.loc[i,"Accreditation ID"])
    reg_input.click()
    reg_input.send_keys(Keys.ENTER)

    driver.find_element(By.XPATH, "//button[text()='Search']").click()

    import time

    time.sleep(5)  # allow Salesforce to render results

    numbers = driver.execute_script("""
    function collect(root, results) {
        if (!root) return;

        root.querySelectorAll('li.search-result-text-style')
            .forEach(li => {
                const text = li.textContent.trim();
                if (text) results.push(text);
            });

        for (const el of root.querySelectorAll('*')) {
            if (el.shadowRoot) {
                collect(el.shadowRoot, results);
            }
        }
    }

    const results = [];
    collect(document, results);
    return results;
    """)

    print(numbers)
    def extract_phone(items):
        for item in items:
            # Case 1: "Phone Number 088497890"
            if item.startswith("Phone Number"):
                parts = item.replace("Phone Number", "").strip()
                if parts:  # number exists
                    return parts
                else:
                    return ''
        return None
    phone = extract_phone(numbers)

    print(f"phone", phone)
    df.loc[i,"phone"] = phone

    link = driver.execute_script("""
    function findResultLink(root) {
        if (!root) return null;

        const a = root.querySelector('a.search-result-name-text-style');
        if (a) return a;

        for (const el of root.querySelectorAll('*')) {
            if (el.shadowRoot) {
                const found = findResultLink(el.shadowRoot);
                if (found) return found;
            }
        }
        return null;
    }
    return findResultLink(document);
    """)

    if not link:
        print("No practitioner found")
    else:
        # driver.execute_script("arguments[0].click();", link)
        print("Opening link:", link.get_attribute("href"))
        address, contact_details = get_practitioner_details(link.get_attribute("href"))
        # go open the link in new tab

    name = link.text.strip()
    href = link.get_attribute("href")
    df.loc[i,"namae"] = name
    df.loc[i,"contact details"] = contact_details
    df.loc[i,"business details"] = address

    i+=1


print(df.head(10))
time.sleep(20)