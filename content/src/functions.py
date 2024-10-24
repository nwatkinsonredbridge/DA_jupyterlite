from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import glob
from selenium.webdriver.chrome.options import Options
import os
import time

###########################

current_directory = os.path.dirname(os.path.abspath(__file__))
driver = None
dfile = None

###########################

def set_global_driver(dr):
    global driver
    driver = dr

def get_dfile(company_name):
    dire_raw = f"{current_directory}/../EXPORT_2023/RAW_CLEANUP/{company_name}/*/reports/"
    g = glob.glob(dire_raw + "*.xhtml")
    if len(g) == 0:
        g = glob.glob(dire_raw+ "*.html")
    try:
        dfile = f"file://{g[0]}"
    except:
        g = glob.glob(dire_raw + "*")
        #print("File not found, file available : ")
        dfile = None
    return dfile

###########################

def get_element_from_varn(varn):
    global driver
    try:
        xpath = f"//*[local-name()='nonFraction' and @name='{varn}']"
        element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        try:
            xpath = f"//*[local-name()='ix:nonFraction' and @name='{varn}']"
            element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))                
        except:
            try:
                xpath = f"//*[local-name()='nonfraction' and @name='{varn}']"
                element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
            except:
                try:
                    xpath = f"//*[local-name()='ix:nonfraction' and @name='{varn}']"
                    element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath)))
                except:
                    #print(f"Element not found: {varn}")
                    return driver, None
    return driver, element

###########################

def go_to_element(element):
    global driver
    attributes = driver.execute_script('''var items = {}; 
                                      for (index = 0; index < arguments[0].attributes.length; ++index) {
                                          items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
                                      }; 
                                      return items;''', element)
    
    try:
        element_id = attributes['id']
    except:
        element_id = driver.execute_script('''
            var parent = arguments[0].parentElement;
            return parent.id;
        ''', element)

    parent_xpath = driver.execute_script('''
        function getXPathForElement(el) {
            var xpath = '';
            for (; el && el.nodeType == 1; el = el.parentNode) {
                var id = Array.prototype.indexOf.call(el.parentNode.childNodes, el) + 1;
                id = (id > 1 ? '[' + id + ']' : '');
                xpath = '/' + el.tagName.toLowerCase() + id + xpath;
            }
            return xpath;
        }
        return getXPathForElement(arguments[0].parentElement);
    ''', element)
    
    script1 = """
        var element = arguments[0];
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        element.scrollBy(0, -200);  // Scroll up by 1 cm (approximately 37.8 pixels)
        """
    driver.execute_script(script1, element)
    time.sleep(1)

    #try:
    #    WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.ID, element_id)))
    #except:
    actions = ActionChains(driver)
    for i in range(2):
        actions.send_keys(Keys.ARROW_UP).perform()
    return element_id, parent_xpath
    
###########################

def highlight(element):
    global driver
    global wait
    parent_element = element.find_element(By.XPATH, "..")
    driver.execute_script("arguments[0].style.backgroundColor = 'yellow';", parent_element)
    return parent_element

###########################

def undo_highlight(element):
    global driver
    global wait

    parent_element = element.find_element(By.XPATH, "..")

    # Reset the background color to an empty value, which will remove the inline style
    driver.execute_script("arguments[0].style.backgroundColor = '';", parent_element)

###########################

class navigate_variables:
    def __init__(self):
        global driver  
        global wait
        wait = WebDriverWait(driver, 2)
  
        self.driver = driver
        self.D_highlighted = {}
    
    def select_var(self, varn):
        try:
            element = select_var_driver(varn)
            if element is not None:
                self.D_highlighted[varn] = element
                return 1
            else:
                return 0
        except:
            return 0
        
    
    def undo_highlight(self, varn):
        if varn in self.D_highlighted.keys():
            _, element = get_element_from_varn(varn)
            undo_highlight(element)




def select_var_driver(varn):
    global wait
    global driver

    try:
        driver, element = get_element_from_varn(varn)
        if element is None:
            return None
        element_id, _ = go_to_element( element)
        
    except:
        print("Unable to go to element.")
        return None        
    try:
        highlight(element)
        return element
    except Exception as e:
        print("Impossible to highlight.")
        return None


##############################

def load_document(company_name = None):
    global driver
    global dfile

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--auto-open-devtools-for-tabs")
 
    if driver is None:
        driver = webdriver.Chrome(options=chrome_options)

    if company_name is not None:
        dfile_loc = get_dfile(company_name)
        if dfile_loc is not None:
            if dfile != dfile_loc:      
                driver.get(dfile_loc)   
                dfile = dfile_loc
                time.sleep(1)
            return 1, dfile
        else:
            return 0, dfile
    
    ###############################
     
    return driver


