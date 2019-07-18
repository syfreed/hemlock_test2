##############################################################################
# AI Participant class
# by Dillon Bowen
# last modified 07/18/2019
##############################################################################

import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class AIParticipant(unittest.TestCase):
    SURVEY_URL = None

    def setUp(self):
        self.driver = webdriver.Chrome()
        
    def test(self):
        driver = self.driver
        driver.get(self.SURVEY_URL)
        while True:
            try:
                elem = driver.find_element_by_id('forward-button')
                print('elem', elem)
                elem.click()
            except:
                return

    # def test_search_in_python_org(self):
        # driver = self.driver
        # driver.get(self.SURVEY_URL)
        # print('dirver title', driver.title)
        # self.assertIn("Python", driver.title)
        # elem = driver.find_element_by_name("q")
        # elem.send_keys("pycon")
        # elem.send_keys(Keys.RETURN)
        # assert "No results found." not in driver.page_source


    def tearDown(self):
        self.driver.close()