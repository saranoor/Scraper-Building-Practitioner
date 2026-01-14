import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pyshadow.main import Shadow
import time

def enrich_bpr_data(outpath="BPR.csv", n_rows=10):
    df = pd.read_csv(outpath)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")

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
    time.sleep(5)

    if not reg_input:
        raise Exception("Registration input not found")

    i=0
    start_time_overall = time.time()
    print(f"Overall start time is; {start_time_overall}")
    while (i<n_rows):
        start_time = time.time()
        # print(f"Processing row {i}")

        reg_input.click()
        reg_input.clear()
        reg_input.send_keys(df.loc[i,"Accreditation ID"])
        reg_input.click()
        reg_input.send_keys(Keys.ENTER)

        driver.find_element(By.XPATH, "//button[text()='Search']").click()

        time.sleep(3)  # allow Salesforce to render results

        shadow = Shadow(driver)

        try:
            link_el = shadow.find_element("a.search-result-name-text-style")
            name = link_el.text.strip()
            link = link_el.get_attribute("href")
        except:
            name, link = "N/A", "N/A"

        try:
            phone = shadow.find_element("span.phone-value-style").text.strip()
        except:
            phone = "N/A"

        driver.execute_script(f"window.open('{link}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        shadow = Shadow(driver)

        found = False
        for attempt in range(10): # Try for 10 seconds total
            all_labels = shadow.find_elements("label[c-practitionerdetail_practitionerdetail]")
            if len(all_labels) > 0:
                found = True
                break
            time.sleep(1)

        address = ""

        for label in all_labels:
            text = label.text.strip()
            
            if text == "Business address":
                # Move up to the container, then to the next sibling container
                parent = shadow.get_parent_element(label) 
                value_item = shadow.get_next_sibling_element(parent)
                address = value_item.text.strip().replace('\n', ', ')

        df.loc[i,"namae"] = name
        df.loc[i,"contact details"] = phone
        df.loc[i,"business details"] = address

        i+=1
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        end_time = time.time()
        print(f"Time for row {i}: ", end_time - start_time)

    print("Time after loop: ", time.time()-start_time_overall)
    df.to_csv("BPR_enriched.csv", index=False)