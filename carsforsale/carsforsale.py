from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import pandas as pd
import csv, os, math, json

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9010")
# chrome_options.add_argument("--headless")  # Ensure GUI is off
# chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
# chrome_options.add_argument("--disable-gpu")  # applicable to windows os only
# chrome_options.add_argument("start-maximized")  # open Browser in maximized mode
# chrome_options.add_argument("disable-infobars")  # disabling infobars
# chrome_options.add_argument("--disable-extensions")  # disabling extensions
# chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
# chrome_options.add_argument('--log-level=3')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

def add_header(file):
  headers = ['Name', 'Price', 'Phone Number']

  # Read the existing content
  with open(file, 'r', encoding='utf-8-sig') as csv_file:
    existing_content = csv_file.readlines()
    # Check if the file is empty or the header does not match
    has_header = len(existing_content) > 0 and existing_content[0].strip().split(',') == headers

  # Write the header followed by the existing content if header is not found
  if not has_header:
    with open(file, 'w', newline='', encoding='utf-8-sig') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow(headers)  # Writing the header
      csv_file.writelines(existing_content)

def remove_duplications(file):
  # Remove duplicated rows
  df = pd.read_csv(file)
  os.remove(file)
  df_unique = df.drop_duplicates(df.columns[2])
  df_unique.to_csv(file, index=False, encoding='utf-8-sig')

def main():
  driver.get(input_url)
  element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'panel-collapser__link-text--dense'))
  )
  brand_elements = driver.find_elements(By.CLASS_NAME, 'panel-collapser__link-text--dense')
  print(f'### {len(brand_elements)} brands found ###')
  brand_urls = []
  brand_urls.extend(brand_element.get_attribute('href') for brand_element in brand_elements)
  for brand_index, brand_url in enumerate(brand_urls):
    if brand_index == 0:
      continue
    driver.get(brand_url)
    brand_name = driver.find_elements(By.CLASS_NAME, 'panel-collapser__link-text--dense')[brand_index].find_element(By.TAG_NAME, 'h5').text
    output_file_name = f'carsforsale_{brand_index + 1}_{brand_name}.csv'
    page_id = 1
    while True:
      driver.get(f'{brand_url}?PageNumber={page_id}')
      if page_id == 1:
        product_num = driver.find_element(By.CLASS_NAME, 'results-count').text.split(' ')[-2]
        print(f'{brand_name} has {product_num} results')
      try:
        if 'Oops! An error occurred!' in driver.find_element(By.CLASS_NAME, 'section-subtitle').text:
          break
      except:
        print(f'--- {brand_index + 1} / {page_id} page ---')
      ld_json_script_element = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')[-1]
      json_str = ld_json_script_element.get_attribute('innerHTML')
      data = json.loads(json_str)
      vehicle_data = []
      for vehicle in data['@graph']:
        vehicle_name = vehicle.get('name', 'N/A')  # Default to 'N/A' if not found
        vehicle_priceCurrency = vehicle['offers'].get('priceCurrency', 'N/A')  # Default to 'N/A' if not found
        vehicle_price = vehicle['offers'].get('price', 'N/A')  # Default to 'N/A' if not found
        if int(vehicle_price) == 0:
          continue
        dealer_telephone = vehicle['offers']['seller'].get('telephone', 'N/A')  # Default to 'N/A' if not found
        
        vehicle_data = [vehicle_name, f'{vehicle_priceCurrency} {vehicle_price}', dealer_telephone]
        open_out = open(output_file_name,'a',newline="", encoding='utf-8-sig')
        file_o_csv = csv.writer(open_out, delimiter=',')
        file_o_csv.writerow(vehicle_data)
        open_out.close()
      page_id += 1
    add_header(output_file_name)
    remove_duplications(output_file_name)
    print(f'The result saved as "{output_file_name}".')

if __name__ == "__main__":
  input_url = 'https://www.carsforsale.com/'
  # output_file_name = ''
  main()