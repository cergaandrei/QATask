from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import pytest
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from tests.helper_functions import search_product, fill_checkout_form, \
    select_shipping_method, place_order, select_product_and_attributes


@pytest.mark.parametrize("product_name, shipping_method", [
    ("jacket", "tablerate_bestway"),
    ("t-shirt", "flatrate_flatrate"),
    ("shorts", "tablerate_bestway"),
])
def test_complete_order_flow(driver, config, product_name, shipping_method):
    search_product(driver, config["base_url"], product_name)
    assert "catalogsearch/result" in driver.current_url, f"Search for {product_name} failed!"

    size, color = select_product_and_attributes(driver)
    assert "shopping cart" in driver.page_source, f"Product ({product_name}) with {size}/{color} was not added to cart!"

    fill_checkout_form(driver, config["user_details"])
    assert driver.find_element("name", "firstname").get_attribute("value") == config["user_details"]["firstname"], "Firstname mismatch!"

    select_shipping_method(driver, shipping_method)
    assert "shipping-method" in driver.page_source, "Failed to select shipping method!"

    place_order(driver)
    assert "Thank you for your purchase!" in driver.page_source, "Order placement failed!"



@pytest.mark.xfail(reason="Expected failure if validation appears")
def test_invalid_email_checkout(driver, config):
    """XFAIL if validation appears for invalid email, XPASS if it does not."""
    product_name = "jacket"
    search_product(driver, config["base_url"], product_name)
    assert "catalogsearch/result" in driver.current_url, f"Search for {product_name} failed!"

    size, color = select_product_and_attributes(driver)
    assert "shopping cart" in driver.page_source, f"Product ({product_name}) with {size}/{color} was not added to cart!"
    invalid_user_details = config["user_details"].copy()
    invalid_user_details["default_email"] = "invalid-email"

    fill_checkout_form(driver, invalid_user_details)

    try:
        error_element = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.ID, "customer-email-error"))
        )
        if error_element.is_displayed():
            pytest.xfail("Validation error appeared as expected!")
    except TimeoutException:
        pass



@pytest.mark.xfail(reason="Expected failure if validation appears")
def test_invalid_postcode_checkout(driver, config):
    """Test checkout with an invalid postcode."""
    product_name = "jacket"
    search_product(driver, config["base_url"], product_name)
    assert "catalogsearch/result" in driver.current_url, f"Search for {product_name} failed!"

    size, color = select_product_and_attributes(driver)
    assert "shopping cart" in driver.page_source, f"Product ({product_name}) with {size}/{color} was not added to cart!"

    invalid_user_details = config["user_details"].copy()
    invalid_user_details["postcode"] = "abcd123"

    fill_checkout_form(driver, invalid_user_details)

    try:
        error_element = driver.find_element(By.XPATH, "//span[@data-bind='text: element.warn']")
        if error_element.is_displayed():
            pytest.xfail("Validation error appeared as expected!")
    except NoSuchElementException:
        pass



