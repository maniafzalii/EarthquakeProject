import time 
import datetime
import pandas as pd
from pathlib import Path
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
BOLD = '\033[1m'
RESET = '\033[0m'


#calculate current date ,but site accept one day ago
def get_max_time():
    date=datetime.datetime.now()-datetime.timedelta(days=1)
    return date.strftime("%Y-%m-%d")

#calculate one month ago
def get_min_time():
    date=datetime.datetime.now()-datetime.timedelta(days=1)
    one_month_ago = date - relativedelta(months=1)
    return one_month_ago.strftime("%Y-%m-%d")

def scrape_emsc():
    all_earthquake_information=[]
    driver=None
    try:
        #options=Options()
        #options.add_argument("--headless")
        driver=webdriver.Firefox()
        wait=WebDriverWait(driver,10)
        driver.get("https://www.emsc.eu/Earthquake_information/")
        driver.maximize_window()
        time.sleep(5)

        #find the cookie and click on it
        try:
            cookie_selector=driver.find_element(By.CSS_SELECTOR,"a[onclick='setCookieConsent();']")
            cookie_selector.click()
        except Exception as ex:
            print(f"{RED}Exception Occured During Scraping EMSC !{RESET}")

        #calculate yesterday and one month ago
        # EMSC does not accept today     
        previous_date=get_min_time() 
        current_date=get_max_time()

        #set min date
        try:
            date_min_box = wait.until(EC.presence_of_element_located((By.ID, 'datemin')))
            driver.execute_script("arguments[0].value = arguments[1];", date_min_box, previous_date)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_min_box)
        except Exception as ex:
            print(f"{RED}Exception Occured During Scraping EMSC !{RESET}")
            
        #set max date    
        try:
            date_max_box = wait.until(EC.presence_of_element_located((By.ID, 'datemax')))
            driver.execute_script("arguments[0].value = arguments[1];", date_max_box, current_date)
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_max_box)
        except Exception as ex:
            print(f"{RED}Exception Occured During Scraping EMSC !{RESET}")
        #set region    
        try:
            search_box=wait.until(EC.element_to_be_clickable((By.ID,'reg')))
            search_box.click()
            search_box.clear()
            time.sleep(0.5)
            search_box.send_keys('japan')
            time.sleep(2)
            search_list = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.prop')))
            select_all=search_list.find_element(By.CLASS_NAME,"checkall")
            select_all.click()
            time.sleep(1)
            send_check=driver.find_element(By.CSS_SELECTOR,'div.prop-send')
            send_check.click()
            time.sleep(1)
        except Exception as ex:
            print(f"{RED}Exception Occured During Scraping EMSC !{RESET}")
            return False


        #click search button
        try:
            submit_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'div.subm input[type="submit"]')))
            submit_button.click()
            time.sleep(2)
        except Exception as ex:
            print(f"{RED}Exception Occured During Scraping EMSC !{RESET}")
            return False


        #find search result
        page_number=1
        all_pages_extracted=False
        while not(all_pages_extracted):
            print(f"Scraping Page {BLUE}{page_number}{RESET} from EMSC")
            try:
                #get element shows result of search and wait until all data loaded
                search_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.htab")))
                #get the table inside div.htab
                table_content= search_content.find_element(By.CSS_SELECTOR, ".eqs.table-scroll")
                #scroll page
                last_height=driver.execute_script("return document.body.scrollHeight")
                while True:
                    driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                    time.sleep(5)
                    new_height=driver.execute_script("return document.body.scrollHeight")
                    if new_height==last_height:
                        break
                    last_height=new_height

                #find data of each row (every earthquake)    
                earthquake_search_data=table_content.find_elements(By.CSS_SELECTOR,'tr')
                for data in earthquake_search_data:
                    date_links = data.find_elements(By.CSS_SELECTOR, 'td.tbdat > a')
                    if not date_links:
                        continue
                    #fetch date
                    try:
                        earthquake_date=date_links[0].text.split('\n')[0].strip()
                        earthquake_latitude=data.find_element(By.CLASS_NAME,'tblat').text
                        earthquake_longitude=data.find_element(By.CLASS_NAME,'tblon').text
                        earthquake_depth=data.find_element(By.CLASS_NAME,'tbdep').text
                        earthquake_magnitude=data.find_element(By.CLASS_NAME,'tbmag').text
                        earthquake_region=data.find_element(By.CLASS_NAME,'tbreg').text
 
                        #save information of each row in a dictionary and append to list of all earthquakes
                        earthquake_info={
                            'time':earthquake_date,
                            'latitude':earthquake_latitude,
                            'longitude':earthquake_longitude,
                            'depth':earthquake_depth,
                            'magnitude':earthquake_magnitude,
                            'place':earthquake_region} 
                        all_earthquake_information.append(earthquake_info)   
                    except Exception as es:
                        print(f"{RED}Exception Occured During Scraping EMSC !{RESET}")
                        continue     
            
                try:
                    next_page = driver.find_element(By.XPATH, "//div[@class='page-cont']//div[contains(@class,'spes') and normalize-space()='›']")
                    next_page_class = next_page.get_attribute("class") or ""

                    if "dis" in next_page_class or "oldpag" in next_page_class:
                        all_pages_extracted = True
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", next_page)
                        page_number += 1
                        time.sleep(3)
                except Exception as e:
                    print(f"{RED}Exception Occured During Scraping EMSC !{RESET}")
                    break
                                                                                                  
            except Exception as ex:
                print(f"{RED}Exception Occured During Scraping EMSC !{RESET}") 
                break
        earthquake_table=pd.DataFrame(all_earthquake_information)    
        #get path and save csv 
        current_path = Path(__file__).resolve()  
        root=current_path.parent.parent
        path=root/'data'/'raw'/'JAPAN_EMSC.csv'
        earthquake_table.to_csv(path,index=False)  
        print("Scrapping Data from EMSC is over !")
        return True     
    except Exception as ex:
        print(f"{RED}Exception Occured During Scraping EMSC !{RESET}")
        return False    
    finally:
        if driver:
            driver.quit()

