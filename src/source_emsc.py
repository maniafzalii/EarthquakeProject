import time 
import datetime
import pandas as pd
from pathlib import Path
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    #options=Options()
    #options.add_argument("--headless")
    driver=webdriver.Firefox()
    driver.get("https://www.emsc.eu/Earthquake_information/")
    driver.maximize_window()
    time.sleep(2)

    try:
        cookie_selector=driver.find_element(By.CSS_SELECTOR,"a[onclick='setCookieConsent();']")
        cookie_selector.click()
        time.sleep(2)
    except Exception as ex:
        print("Exception:Cookie Not Found! ",ex)    
    previous_date=get_min_time() 
    current_date=get_max_time()
    wait = WebDriverWait(driver, 5)

    #set min date
    try: 
        date_min_box = wait.until(EC.presence_of_element_located((By.ID, 'datemin')))
        driver.execute_script("arguments[0].value = arguments[1];", date_min_box, previous_date)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_min_box)
    except Exception as ex:
        print("Exception:Start Date Entrance Failed! ", ex)
    #set max date    
    try: 
        date_max_box = wait.until(EC.presence_of_element_located((By.ID, 'datemax')))
        driver.execute_script("arguments[0].value = arguments[1];", date_max_box, current_date)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_max_box)
    except Exception as ex:
        print("Exception!End Date Entrance Failed! ", ex)   
    #set region    
    try:
        search_box=driver.find_element(By.ID,'reg')
        search_box.send_keys('japan')
        time.sleep(0.5)
        search_list=driver.find_element(By.CSS_SELECTOR,'div[class="prop"]')
        select_all=search_list.find_element(By.CLASS_NAME,"checkall")
        select_all.click()
        time.sleep(1)
        send_check=search_list.find_element(By.CSS_SELECTOR,'div[class="prop-send"]')
        send_check.click()
        time.sleep(1)
    except Exception as ex:
        print("Exception:Search Process Failed!  ",ex)    

    #click search button    
    try:    
        button_sheet=driver.find_element(By.CSS_SELECTOR,'div[class="subm"]')
        submit_button=button_sheet.find_element(By.CSS_SELECTOR,'input[type="submit"]')
        submit_button.click()
        time.sleep(0.5)
    except Exception as ex:
        print("Exception:Search Button Not Found! ",ex)  

    #find search result
    page_number=1
    all_pages_extracted=False
    while not(all_pages_extracted):
        print(f"Scraping Page  {page_number}")
        try:
            search_content=driver.find_element(By.CSS_SELECTOR,'div[class="htab"]')
            table_content=search_content.find_element(By.CLASS_NAME,'eqs.table-scroll')
            time.sleep(0.1)
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
                #fetch date
                try:
                    earthquake_date_full=data.find_element(By.CSS_SELECTOR,'td.tbdat>a')
                    earthquake_date=earthquake_date_full.text.split('\n')[0].strip()
                    earthquake_latitude=data.find_element(By.CLASS_NAME,'tblat').text
                    earthquake_longitude=data.find_element(By.CLASS_NAME,'tblon').text
                    earthquake_depth=data.find_element(By.CLASS_NAME,'tbdep').text
                    earthquake_magnitude=data.find_element(By.CLASS_NAME,'tbmag').text
                    earthquake_region=data.find_element(By.CLASS_NAME,'tbreg').text
 
                    #save information of each row in a dictionary and append to list of all earthquakes
                    earthquake_info={'time ':earthquake_date,'latitude ':earthquake_latitude,'longtitude ':earthquake_longitude,'depth ':earthquake_depth,
                             'magnitude ':earthquake_magnitude,'place ':earthquake_region} 
                    all_earthquake_information.append(earthquake_info)   
                except Exception as es:
                    print("Exception:Earthquake Data Not Found!  ",es)  
                    continue     
            
            try:
                next_page = driver.find_element(By.XPATH, "//div[@class='page-cont']/div[contains(@class, 'spes') and text()='›']")
                if "dis" in next_page.get_attribute("class"):
                    #all pages extracted
                    all_pages_extracted = True
                else:
                    next_page.click()
                    #driver.execute_script("arguments[0].click();", next_page)
                    page_number += 1
                    time.sleep(3) 
            except Exception as e:
                print("Exception:Next Page Not Found! ", e)  
                all_pages_extracted=True  
                                                                                                  
        except Exception as ex:
            print("Exception Fetch Content Unseccesful ",ex)  
    erathquake_table=pd.DataFrame(all_earthquake_information)    
    #get path and save csv 
    current_path = Path(__file__).resolve()  
    root=current_path.parent.parent
    path=root/'data'/'raw'/'JAPAN_EMSC.csv'
    erathquake_table.to_csv(path,index=False)
    driver.quit()    

scrape_emsc()