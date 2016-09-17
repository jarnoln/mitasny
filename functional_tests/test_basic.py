import time
from .functional_test import FunctionalTest


class MitasnyBasicTest(FunctionalTest):
    def test_basic_use(self):
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 1024)
        time.sleep(1)
        self.assertIn('Django', self.browser.title)

