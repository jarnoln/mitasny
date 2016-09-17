from unittest import TestCase
# from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# class FunctionalTest(LiveServerTestCase):
class FunctionalTest(TestCase):
    def setUp(self):
        self.server_url = 'http://localhost:8000'
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

