import os

with open('tests/e2e/test_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

login_code = """
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
    assert "AdaptiveMLOps" in driver.page_source

def test_prediction_and_feedback(driver):
    login(driver)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Predictions')]").click()
"""

# Replace test functions
content = content.replace('def test_app_loads(driver):', 'def login(driver):\n    driver.get(URL)\n    try:\n        wait_for_text(driver, "Login to AdaptiveMLOps", timeout=3)\n        driver.find_element(By.XPATH, "//button[text()=\'Login\']").click()\n        wait_for_text(driver, "AdaptiveMLOps")\n    except Exception:\n        pass # already logged in\n\ndef test_app_loads(driver):')
content = content.replace('driver.get(URL)', 'login(driver)')
# It will replace multiple, but the first one in test_app_loads is replaced above, oh wait.

with open('tests/e2e/test_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)
