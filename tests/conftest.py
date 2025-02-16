import json
import pytest
from selenium import webdriver

@pytest.fixture(scope="session")
def config():
    """Load test configuration from JSON file."""
    with open("config.json", "r") as file:
        return json.load(file)

@pytest.fixture(scope="function")
def driver():
    """Initialize WebDriver and clean up after each test."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()
