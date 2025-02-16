import logging
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def wait_for_element(driver, by, value, timeout=10, condition=EC.presence_of_element_located):
    return WebDriverWait(driver, timeout).until(condition((by, value)))

def search_product(driver, base_url, product_name):
    """Search for a product dynamically."""
    logging.info(f"Searching for product: {product_name}")
    driver.get(f"{base_url}/")
    search_box = wait_for_element(driver, By.NAME, "q", condition=EC.element_to_be_clickable)
    search_box.send_keys(product_name + "\n")


def select_product_and_attributes(driver):
    """Searches for a product, clicks it, selects available size and color dynamically, and adds it to the cart."""

    # Step 1: Click on the first product in the search results
    product_list = driver.find_elements(By.CSS_SELECTOR, "a.product-item-link")
    if not product_list:
        raise Exception("No products found in search results!")

    product_list[0].click()  # Click first product

    # Wait for the product details page to load
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-info-main"))
    )

    selected_color, selected_size = None, None

    # Step 2: Select size if available
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.swatch-option.text"))
        )
        size_elements = driver.find_elements(By.CSS_SELECTOR, "div.swatch-option.text")

        if size_elements:
            selected_size = size_elements[0]
            driver.execute_script("arguments[0].click();", selected_size)
        else:
            print("No size selection required for this product.")

    except:
        print("No size options found, skipping selection.")

    # Step 3: Select color if available
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.swatch-option.color"))
        )
        color_elements = driver.find_elements(By.CSS_SELECTOR, "div.swatch-option.color")

        if color_elements:
            selected_color = color_elements[0]
            driver.execute_script("arguments[0].click();", selected_color)
        else:
            print("No color selection required for this product.")

    except:
        print("No color options found, skipping selection.")

    # Step 4: Click "Add to Cart" button
    add_to_cart_button = driver.find_element(By.CSS_SELECTOR, "button#product-addtocart-button")
    driver.execute_script("arguments[0].click();", add_to_cart_button)

    # Step 5: Wait for the correct "added to cart" message
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-bind*='prepareMessageForHtml']"))
    )

    return selected_size.text if selected_size else "No size", selected_color.text if selected_color else "No color"


def fill_checkout_form(driver, user_details):
    """Dynamically fill the checkout form with values from config using stable 'name' attributes."""
    logging.info("Filling out checkout form...")
    driver.get("https://magento.softwaretestingboard.com/checkout/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "form#co-shipping-form"))
    )

    # ✅ Function to fill fields safely
    def fill_field(field_name, value):
        field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, field_name))
        )
        field.clear()
        field.send_keys(value)
        time.sleep(1)  # Short delay to ensure input registers

    email_field = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "customer-email"))  # Using ID for better targeting
    )
    email_field.click()
    email_field.send_keys(user_details["default_email"])
    fill_field("firstname", user_details["firstname"])  # First Name
    fill_field("lastname", user_details["lastname"])  # Last
    fill_field("street[0]", user_details["street"])  # Street Address
    fill_field("city", user_details["city"])  # City
    fill_field("postcode", user_details["postcode"])  # Zip Code
    fill_field("telephone", user_details["telephone"])  # Phone Number

    # ✅ Select State Dropdown
    state_dropdown = Select(WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "region_id"))
    ))
    state_dropdown.select_by_visible_text(user_details["region"])  # Select by text (e.g., "California")
    time.sleep(5)  # Delay to allow state selection to register

    # ✅ Select Country Dropdown
    country_dropdown = Select(WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "country_id"))
    ))
    country_dropdown.select_by_visible_text(user_details["country"])  # Select country (e.g., "United States")
    time.sleep(5)  # Ensure country selection registers

    logging.info("✅ Checkout form filled successfully.")


def select_shipping_method(driver, shipping_method):
    """Select a dynamic shipping method."""
    logging.info(f"Selecting shipping method: {shipping_method}")
    shipping_option = wait_for_element(driver, By.CSS_SELECTOR, f"input[type='radio'][value='{shipping_method}']", timeout=15)
    shipping_option.click()
    wait_for_element(driver, By.CSS_SELECTOR, "button[data-role='opc-continue']", timeout=15).click()

def place_order(driver):
    """Dynamically place the order after ensuring the loading icon disappears."""
    logging.info("Placing the order...")
    time.sleep(10)
    # Wait for loading icon to disappear (replace with actual class name or ID of the spinner)
    WebDriverWait(driver, 15).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "loading-mask"))  # Update this if needed
    )

    # Wait for Place Order button to be clickable
    place_order_button = wait_for_element(driver, By.XPATH, "//span[text()='Place Order']", condition=EC.element_to_be_clickable, timeout=15)
    place_order_button.click()
    time.sleep(5)
    logging.info("✅ Order placed successfully.")

