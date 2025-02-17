from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
import random
import string
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def wait_for_element(driver, by, value, timeout=10, condition=EC.presence_of_element_located):
    return WebDriverWait(driver, timeout).until(condition((by, value)))

def generate_random_email():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"testuser_{random_string}@example.com"

def generate_secure_password(length=12):
    uppercase = random.choice(string.ascii_uppercase)
    lowercase = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*")

    remaining_chars = "".join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=length - 4))

    password = uppercase + lowercase + digit + special + remaining_chars
    return "".join(random.sample(password, len(password)))

def create_account(driver, base_url, user_details):
    logging.info("Starting account creation process...")
    time.sleep(5)
    driver.get(base_url + "/customer/account/create/")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "firstname"))
    )

    def fill_field(field_name, value):
        field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, field_name))
        )
        field.clear()
        field.send_keys(value)
        time.sleep(1)

    email_field = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "email_address"))
    )
    email_field.click()
    user_details["default_email"] = generate_random_email()
    fill_field("email", user_details["default_email"])
    fill_field("firstname", user_details["firstname"])
    fill_field("lastname", user_details["lastname"])

    password = generate_secure_password()
    fill_field("password", password)
    fill_field("password_confirmation", password)

    logging.info(f"Generated Password: {password}")

    create_account_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.action.submit.primary"))
    )
    create_account_button.click()

    logging.info("Account creation process completed.")



def search_product(driver, base_url, product_name):
    logging.info(f"Searching for product: {product_name}")
    driver.get(f"{base_url}/")
    search_box = wait_for_element(driver, By.NAME, "q", condition=EC.element_to_be_clickable)
    search_box.send_keys(product_name + "\n")


def select_product_and_attributes(driver):

    product_list = driver.find_elements(By.CSS_SELECTOR, "a.product-item-link")
    if not product_list:
        raise Exception("No products found in search results!")

    product_list[0].click()


    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-info-main"))
    )

    selected_color, selected_size = None, None


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

    return selected_size.text if selected_size else "No size", selected_color.text if selected_color else "No color"

def add_to_cart(driver):
    add_to_cart_button = wait_for_element(driver, By.CSS_SELECTOR, "button.tocart", condition=EC.element_to_be_clickable)
    add_to_cart_button.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.message-success"))
    )
    time.sleep(5)
def fill_checkout_form(driver, user_details):
    logging.info("Filling out checkout form...")
    driver.get("https://magento.softwaretestingboard.com/checkout/")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "form#co-shipping-form"))
    )

    def fill_field(field_name, value):
        try:
            field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, field_name))
            )
            field.clear()
            field.send_keys(value)
            time.sleep(1)
        except TimeoutException:
            logging.warning(f"Field '{field_name}' not found. Skipping...")

    try:
        email_field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "customer-email"))
        )

        if email_field.is_displayed() and email_field.is_enabled():
            email_field.clear()
            email_field.send_keys(user_details["default_email"])
            logging.info(f"Entered email: {user_details['default_email']}")
        else:
            logging.info("Email field is present but not interactable. Skipping it.")
    except TimeoutException:
        logging.info("Email field not found. Assuming user is logged in and skipping it.")

    fill_field("firstname", user_details["firstname"])
    fill_field("lastname", user_details["lastname"])
    fill_field("street[0]", user_details["street"])
    fill_field("city", user_details["city"])
    fill_field("postcode", user_details["postcode"])
    fill_field("telephone", user_details["telephone"])

    try:
        state_dropdown = Select(WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "region_id"))
        ))
        state_dropdown.select_by_visible_text(user_details["region"])
    except TimeoutException:
        logging.warning("State dropdown not found. Skipping...")

    try:
        country_dropdown = Select(WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "country_id"))
        ))
        country_dropdown.select_by_visible_text(user_details["country"])
    except TimeoutException:
        logging.warning("Country dropdown not found. Skipping...")

    logging.info("Checkout form filled successfully.")





def select_shipping_method(driver, shipping_method):
    logging.info(f"Selecting shipping method: {shipping_method}")

    wait = WebDriverWait(driver, 15)

    wait.until(EC.presence_of_element_located((By.XPATH, f"//input[@type='radio' and @value='{shipping_method}']")))
    shipping_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[@type='radio' and @value='{shipping_method}']")))

    if not shipping_option.is_selected():
        driver.execute_script("arguments[0].click();", shipping_option)
        logging.info(f"Clicked on shipping method: {shipping_method}")
    else:
        logging.info(f"Shipping method {shipping_method} was already selected")

    continue_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-role='opc-continue']")))
    driver.execute_script("arguments[0].click();", continue_button)
    logging.info("Clicked on 'Continue' button")


def place_order(driver):
    logging.info("Placing the order...")
    time.sleep(10)
    WebDriverWait(driver, 15).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "loading-mask"))
    )

    place_order_button = wait_for_element(driver, By.XPATH, "//span[text()='Place Order']", condition=EC.element_to_be_clickable, timeout=15)
    place_order_button.click()
    time.sleep(5)
    logging.info("Order placed successfully.")


def hover_and_click_tees(driver):
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    women_menu = wait.until(EC.presence_of_element_located((By.ID, "ui-id-4")))
    actions.move_to_element(women_menu).perform()

    tops_menu = wait.until(EC.presence_of_element_located((By.ID, "ui-id-9")))
    actions.move_to_element(tops_menu).perform()

    tees_option = wait.until(EC.element_to_be_clickable((By.ID, "ui-id-13")))
    tees_option.click()

    print("Successfully navigated to Tees!")



def change_quantity(driver, quantity=4):
    wait = WebDriverWait(driver, 10)

    qty_input = wait.until(EC.presence_of_element_located((By.ID, "qty")))

    qty_input.clear()
    qty_input.send_keys(str(quantity))

    print(f"Quantity changed to {quantity}")

def verify_discount_applied(driver):
    try:
        logging.info("Verifying discount application...")

        discount_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.price[data-th*='discount']"))
        )
        discount_value = discount_element.text.strip()

        if discount_value.startswith("-$"):  # Ensure it's a negative discount
            logging.info(f"Discount applied successfully: {discount_value}")
            return True
        else:
            logging.warning(f"Unexpected discount value: {discount_value}")
            return False

    except Exception as e:
        logging.error(f"Failed to verify discount: {str(e)}")
        return False

