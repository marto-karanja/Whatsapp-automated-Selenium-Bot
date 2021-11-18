# implementing explicit wait

from logging import debug, log

import os
import random
import winsound
import sys
import wx

from time import sleep

# import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium import webdriver  
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import ElementNotVisibleException


class Whatsappbot(object):
    def __init__(self, settings = None, logger = None):
        """Set up class"""
        self.logger = logger
        #self.logger.info("Initializing browser instance")
        # Set up gecko driver
        """
        CHROME_DRIVER = settings['chromedriver']
        self.BID_STATUS = settings['bid_status']
        self.DELAY = settings['delay']"""

        # Launch firefox instance
        
        self.launch_gecko()

        # fetch url
        url = "https://web.whatsapp.com/"
        self.driver.get(url)

    def launch_gecko(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("--incognito")



        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities["marionette"] = True

        driver_url = "driver/geckodriver.exe"
        GECKO_DRIVER = self.resource_path(driver_url)

        # run firefox webdriver from executable path 
        self.driver = webdriver.Firefox(options=options, capabilities=firefox_capabilities, executable_path = GECKO_DRIVER)




    def launch_chrome(self):
        CHROME_DRIVER = "driver/chromedriver.exe"
        CHROME_DRIVER = self.resource_path(CHROME_DRIVER)
        print(CHROME_DRIVER)

        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']);
        #chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('log-level=1') 
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=CHROME_DRIVER)


    """def post_message(self, payload):
        for group, message in payload:
            # identify group
            # refresh window
            self.driver.refresh()
            ## search for group
            try:
                group_link = self.driver.find_element_by_xpath("//span[contains(@class, 'emoji-texttt _ccCW FqYAR i0jNr') and text() = 'Account Verification Docu']")
                group_link.click()
            except NoSuchElementException:

            ### scroll and search for group
            ## scroll through the view finder to find the group
            #post message to group
        pass"""

    #-----------------------------------------------------------------------------
    def resource_path(self, relative_path):

        try:
            base_path = sys._MEIPASS
            
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)
    #-----------------------------------------------------------------------------
    
    def send_message(self, group_name, message, window = None):
        self.find_group(group_name, window)
        # send message
        #message_field = self.driver.find_element_by_xpath("//div[contains(@class,'_1UWac _1LbR4')]//div[contains(@class, '_13NKt copyable-text selectable-text')]")
        #message_field.send_keys(message)
        # click send
        return True
    
    #------------------------------------------------------------------------------ 
    def send_messages(self, pipeline, event, window, group_names, message):
        """Sends messages to multiple groups"""
        counter = 0
        while not event.isSet():
            self.send_message(group_names[counter], message, window)
            if counter == len(group_names) -1:
                event.set()
                wx.CallAfter(window.log_message_to_txt_field, "Finished Posting Process")
            counter = counter + 1


    #-----------------------------------------------------------------------------
    def find_group(self, group_name, window):
        msg = "Searching for group: {}".format(group_name)
        wx.CallAfter(window.log_message_to_txt_field, msg)
        self.driver.refresh()
        try:
            WebDriverWait(self.driver, 240).until(EC.visibility_of_any_elements_located((By.ID, "pane-side")))
        except (ElementNotVisibleException, NoSuchElementException, TimeoutException) as e:
            self.driver.save_screenshot("error_file.png")
        
        xpath_element = "//*[@id='pane-side']"
        chat_body = self.driver.find_element_by_xpath(xpath_element)
        # ensure that you are at the top of the scrollable div
        self.driver.execute_script("arguments[0].scrollIntoView();", chat_body)
        scroll = True
        counter = 0
        while scroll:  # this will scroll 3 times
            try:
                xpath_string = "//span[contains(@class, 'emoji-texttt _ccCW FqYAR i0jNr') and text() = '{}']".format(group_name)
                WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, xpath_string)))
                group_link = self.driver.find_element_by_xpath(xpath_string)
                group_link.click()
            except (NoSuchElementException, TimeoutException) as e:
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',chat_body)
            else:
                #group_link = driver.find_element_by_xpath("//span[contains(@class, 'emoji-texttt _ccCW FqYAR i0jNr') and text() = 'AWWB Kikuyu']")
                #group_link.click()
                print("Element found and clicked", group_name)
                msg = "Group found and clicked: {}".format(group_name)
                wx.CallAfter(window.log_message_to_txt_field, msg)
                scroll = False
                break
            # add appropriate wait here, of course. 1-2 seconds each
            # get current point in log field
            message = "[{}] : Searching for group....".format(group_name)
            if counter == 0:
                wx.CallAfter(window.log_message_to_txt_field, message)
            else:
                insertion_point = (window.logTxtField.GetInsertionPoint() - 1)
                from_point = insertion_point - len(message)
                wx.CallAfter(window.log_message_to_txt_field, message)
            print ("Searching for group", group_name)
            
            # check if at the bottom
            try:
                x = self.driver.find_element_by_xpath("//span[contains(@class, 'emoji-texttt _ccCW FqYAR i0jNr') and text() = 'Futa live']")
                
            except NoSuchElementException:
                # pause
                #sleep(0.1)
                pass
            else:
                x.click()
                print("Group not found, exiting search loop")
                message = "[{}] : Unable to find group".format(group_name)
                wx.CallAfter(window.log_message_to_txt_field, message)
                # break out of the loop when element is present
                scroll = False
