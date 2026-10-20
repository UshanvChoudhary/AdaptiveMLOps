import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import os

# Note: This test requires both backend (8000) and frontend (5173) to be running.
# It also requires a valid webdriver (e.g., ChromeDriver) installed and in PATH.

@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.mark.skipif(not os.environ.get("RUN_E2E"), reason="Requires active frontend/backend and webdriver")
def test_prediction_and_feedback_flow(driver):
    # 1. User navigates to the app
    driver.get("http://localhost:5173")
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    
    assert "AdaptiveMLOps" in driver.page_source
    
    # 2. User enters ticket
    text_area = driver.find_element(By.TAG_NAME, "textarea")
    text_area.send_keys("I need help resetting my password")
    
    # 3. User clicks Get Prediction
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Get Prediction')]")
    submit_btn.click()
    
    # 4. Receives prediction, sees confidence and model version
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "prediction-card"))
    )
    
    assert "Prediction Result" in driver.page_source
    assert "Predicted Label:" in driver.page_source
    assert "Confidence:" in driver.page_source
    assert "Model Version:" in driver.page_source
    
    # 5. User submits feedback (Incorrect)
    incorrect_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Incorrect')]")
    incorrect_btn.click()
    
    # 6. Corrected-label selector/input appears
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "select"))
    )
    
    select_element = Select(driver.find_element(By.TAG_NAME, "select"))
    select_element.select_by_value("technical_support")
    
    submit_correction_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit Correction')]")
    submit_correction_btn.click()
    
    # 7. Feedback confirmation appears
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "feedback-success"))
    )
    
    assert "Thank you for your feedback!" in driver.page_source
