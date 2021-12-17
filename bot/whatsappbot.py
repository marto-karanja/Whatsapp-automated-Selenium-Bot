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
from selenium.webdriver.common.keys import Keys
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

        self.post = False
        self.last_group = "Futa live"

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
    
    def send_message(self, group_name, window = None):
        self.find_group(group_name, window)

    
    
    #------------------------------------------------------------------------------ 
    def send_messages(self, pipeline, event, window, group_names, message):
        """Sends messages to multiple groups"""
        counter = 0
        while not event.isSet():
            self.send_message(group_names[counter], window)
            if self.post:
                self.post_message(group_names[counter], message,window)
            if counter == len(group_names) -1:
                event.set()
                wx.CallAfter(window.log_message_to_txt_field, "Finished Posting Process")
                msg = "-"*30
                wx.CallAfter(window.log_message_to_txt_field, msg)
            counter = counter + 1




#------------------------------------------------------------------------------ 
    def schedule_messages(self, pipeline, event, window, group_names, message, interval, workload):
        """Sends messages to multiple groups"""
        step = interval
        counter = 0
        while not event.isSet():
            while interval < workload:
                while counter != len(group_names):
                    self.send_message(group_names[counter], window)
                    if self.post:
                        self.post_message(group_names[counter], message,window)
                    if counter == len(group_names) -1:
                        #event.set()
                        wx.CallAfter(window.log_message_to_txt_field, "Finished Posting Process")
                        msg = "-"*30
                        wx.CallAfter(window.log_message_to_txt_field, msg)
                        break
                    counter = counter + 1
                msg = "Pausing execution for {0} secs".format(step)
                wx.CallAfter(window.log_message_to_txt_field, msg)
                sleep(step)
                interval = interval + step
            wx.CallAfter(window.log_message_to_txt_field, "Finished Scheduling messages")
            msg = "-"*50
            wx.CallAfter(window.log_message_to_txt_field, msg)








    #-----------------------------------------------------------------------------
    def find_group(self, group_name, window):
        msg = "Searching for group: [{0}]".format(group_name)
        wx.CallAfter(window.log_message_to_txt_field, msg)
        try:
            xpath_element =  "//span[contains(@class, 'emoji-texttt _ccCW FqYAR i0jNr') and text() = '" + group_name + "']"
            group = self.driver.find_element_by_xpath(xpath_element)
        except NoSuchElementException:
            msg = "[{0}] searching....".format(group_name)
            wx.CallAfter(window.log_message_to_txt_field, msg)
            self.driver.execute_script("var myElement = document.getElementById('pane-side');var topPos = myElement.offsetTop;document.getElementById('pane-side').scrollTop = topPos;")
        except StaleElementReferenceException:
            self.driver.refresh()
            self.find_group(group_name, window)
        else:
            group.click()
            self.post = True
            msg = "{0} found and clicked".format(group_name)
            wx.CallAfter(window.log_message_to_txt_field, msg)
            return
    
        
        xpath_element = "//*[@id='pane-side']"
        chat_body = self.driver.find_element_by_xpath(xpath_element)
        for i in range(1,10000):
            
            try:
                xpath_element =  "//span[contains(@class, 'emoji-texttt _ccCW FqYAR i0jNr') and text() = '" + group_name + "']"
                group = self.driver.find_element_by_xpath(xpath_element)
            except NoSuchElementException:
                msg = "[{0}] searching....".format(group_name)
                wx.CallAfter(window.log_message_to_txt_field, msg)
                sleep(1)
            except StaleElementReferenceException:
                self.driver.refresh()
                self.find_group(group_name, window)
            else:
                group.click()
                self.post = True
                msg = "{0} found and clicked".format(group_name)
                wx.CallAfter(window.log_message_to_txt_field, msg)
                break
            try:
                xpath_element = "//span[contains(@class, 'emoji-texttt _ccCW FqYAR i0jNr') and text() = '" + self.last_group + "']"
                x = self.driver.find_element_by_xpath(xpath_element)
                                
            except NoSuchElementException:
                pass
            else:
                x.click()
                print("Group not found, exiting search loop")
                msg = "[{0}] not found".format(group_name)
                wx.CallAfter(window.log_message_to_txt_field, msg)
                break
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + document.body.scrollHeight;',chat_body)

    #------------------------------------------------------------------
    def post_message(self, group_name, message, window):
        print("Sending message {0}".format(message))
        message_field = self.driver.find_element_by_xpath("//div[contains(@class,'_1UWac _1LbR4')]//div[contains(@class, '_13NKt copyable-text selectable-text')]")
        for line in message:
            message_field.send_keys(line)
            message_field.send_keys(Keys.SHIFT + Keys.ENTER)
        message_field.send_keys(Keys.ENTER)
        # send message
        #send_button = self.driver.find_element_by_class_name("_4sWnG")
        #send_button.click()
        msg = "Posted to group [{0}]".format(group_name)
        wx.CallAfter(window.log_message_to_txt_field, msg)

    


    #------------------------------------------------------------------------

    def stop_bot(self):
        """Exit and clean up function"""
        self.driver.quit()

