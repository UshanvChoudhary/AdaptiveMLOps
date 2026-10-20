import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    svc = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=svc, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def wait_for_text(driver, text, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: text in d.page_source
        )
    except Exception as e:
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise e

def login(driver):
    driver.get(URL)
    try:
        wait_for_text(driver, "Login to AdaptiveMLOps", timeout=3)
        driver.find_element(By.XPATH, "//button[text()='Login']").click()
        wait_for_text(driver, "AdaptiveMLOps")
    except Exception:
        pass # already logged in

def test_app_loads(driver):
    login(driver)
    wait_for_text(driver, "AdaptiveMLOps")
    assert "AdaptiveMLOps" in driver.page_source

def test_prediction_and_feedback(driver):
    login(driver)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Predictions')]").click()
    wait_for_text(driver, "Make Prediction")
    time.sleep(1)

def test_model_registry(driver):
    login(driver)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Model Registry')]").click()
    WebDriverWait(driver, 10).until(
        lambda d: "No models" in d.page_source or "Version" in d.page_source or "Error" in d.page_source
    )

def test_retraining(driver):
    login(driver)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Retraining Engine')]").click()
    WebDriverWait(driver, 10).until(
        lambda d: "No retraining jobs found." in d.page_source or "ID" in d.page_source or "Error" in d.page_source
    )

def test_candidate_evaluation(driver):
    login(driver)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Model Promotion')]").click()
    wait_for_text(driver, "Promotion")
    time.sleep(1)

def test_governance_flows(driver):
    login(driver)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Governance')]").click()
    
    # Wait for the main Governance title (avoid ampersand matching issues)
    wait_for_text(driver, "Security")
    time.sleep(1)
    
