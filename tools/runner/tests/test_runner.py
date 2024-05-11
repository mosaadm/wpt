import pytest
import subprocess
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# Constants for URLs and paths
BASE_URL = "http://web-platform.test:8000/tools/runner/index.html"
TEST_PATH = "/dom/abort/AbortSignal.any.html"

# Elements
TEST_PATH_INPUT_FIELD = (By.ID, 'path')
START_BUTTON = (By.XPATH, '//button[text()="Start"]')
DONE_PROGRESS_BAR = (By.CLASS_NAME, "done")
TABLE_CELLS_PASSED = (By.XPATH, '//td[@class="PASS"]')

@pytest.fixture
def driver():
    """
    Sets up before and cleans up after the test.
    """
    # Start the server as a background process
    server_proc = subprocess.Popen(['./wpt', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(20)  # Wait a few seconds to ensure the server is up
    # Options are for CI crash
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    yield driver
    driver.quit()
    server_proc.terminate()
    server_proc.wait() 

def take_screenshot(driver, test_name):
    """
    Takes a screenshot of the current state of the browser.
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"tools/runner/tests/screenshots/{test_name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot saved to {filename}")
    
def test_runner_smoke(driver):
    """
    Navigates to a web platform test runner and runs specific tests,
    checking for the presence of 'Done!' and at least one 'PASS'.
    """
    driver.get(BASE_URL)  
    test_path_input_field = driver.find_element(*TEST_PATH_INPUT_FIELD)
    test_path_input_field.clear()
    test_path_input_field.send_keys(TEST_PATH)
    driver.find_element(*START_BUTTON).click()
    done = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((DONE_PROGRESS_BAR)))
    assert done.text == 'Done!', "Expected to find 'Done!' text when tests are completed."

    passes = driver.find_elements(*TABLE_CELLS_PASSED)
    assert len(passes) > 1, f"Expected table cells to have more than one 'PASS', found {len(passes)}."

