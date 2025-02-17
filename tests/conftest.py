import json
import pytest
from selenium import webdriver

@pytest.fixture(scope="session")
def config():
    with open("config.json", "r") as file:
        return json.load(file)

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()
