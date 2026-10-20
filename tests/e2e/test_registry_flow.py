import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
def test_registry_tab_and_models_flow(driver):
    # 1. User navigates to the app
    driver.get("http://localhost:5173")
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    
    # 2. Click on Model Registry Tab
    registry_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Model Registry')]")
    registry_tab.click()
    
    # 3. Wait for registry container
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "registry-container"))
    )
    
    # 4. Check if the table loads properly
    assert "Model Registry" in driver.page_source
    
    # Check if table headers exist
    assert "Version" in driver.page_source
    assert "Algorithm" in driver.page_source
    assert "Dataset" in driver.page_source
    assert "Training Date" in driver.page_source
    assert "Git Commit" in driver.page_source
    assert "Status" in driver.page_source
    assert "Metrics" in driver.page_source
    assert "Artifact" in driver.page_source
    
    # We don't strictly assert the exact data since db might be empty or seeded differently,
    # but we assert the structure is present
    
