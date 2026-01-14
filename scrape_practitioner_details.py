from selenium import webdriver
from pyshadow.main import Shadow
import time 

def get_practitioner_details(link):
    driver = webdriver.Chrome()
    print(f"type of link: {type(link)}")
    # driver.get("https://bams.vba.vic.gov.au/bams/s/practitioner-detail?inputParams=hP%2Bs9upvYQh4lOvm2Py16w4sob6efCqpS%2FA5BLFdMXmEkOVRlpRAv1T4m0dwvISQ")
    driver.get(link)
    # Initialize Shadow helper
    shadow = Shadow(driver)

    time.sleep(3)  # Wait for the page to load completely
    all_labels = shadow.find_elements("label[c-practitionerdetail_practitionerdetail]")

    address = ""
    phone = ""

    for label in all_labels:
        text = label.text.strip()
        
        if text == "Business address":
            # Move up to the container, then to the next sibling container
            parent = shadow.get_parent_element(label) 
            value_item = shadow.get_next_sibling_element(parent)
            address = value_item.text.strip().replace('\n', ', ')
            
        elif text == "Contact Details":
            # Same logic for Contact Details
            parent = shadow.get_parent_element(label)
            value_item = shadow.get_next_sibling_element(parent)
            phone = value_item.text.strip()

    print(f"Address: {address}")
    print(f"Phone: {phone}")
    return address, phone