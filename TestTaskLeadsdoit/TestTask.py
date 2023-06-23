import base64
import string
import random
import logging
import argparse
import time
import requests
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException


'''Logging'''

parser = argparse.ArgumentParser(description="Run application")
parser.add_argument("--log", action="store_true", help="Enable console logging")
args = parser.parse_args()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if args.log:
    log_filename = 'app.txt'
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)


'''Desired Capabilities'''

desired_caps = {
    'platformName': 'Android',
    'platformVersion': '12.0',
    'deviceName': 'Android Emulator',
    'app': '/Users/vlad/AndroidStudioProjects/MyApplication/app/build/outputs/apk/release/app-release-unsigned.apk',
    'appPackage': 'com.example.myapplication',
    'appActivity': 'com.example.myapplication.MainActivity',
    'automationName': 'UiAutomator2',
    'avd': 'Pixel_6_Pro_API_34',
    'chromedriverExecutable': '/usr/local/Caskroom/chromedriver/chromedriver_mac64/chromedriver',
    'uiautomator2ServerInstallTimeout': 60000
}

'''Locators'''

LOCATORS = {
    'webview_button': (MobileBy.ID, "button"),
    'register_button': (MobileBy.XPATH, "//button[2][@aria-label='Реєстрація']"),
    'email_registration_tab': (MobileBy.XPATH, "//div[2][@class='tabs--tab']"),
    'email_input_field': (MobileBy.XPATH, "//*[@id='Register.email']"),
    'password_input_field': (MobileBy.XPATH, "//*[@id='Register.password']"),
    'register_submit_button': (MobileBy.XPATH, "//*[@id='Register.submit']"),
    'deposit_button': (MobileBy.XPATH, "//div[8]/div[2]/div/div/div/div[1]/span"),
    'deposit_pop_up_close_button': (MobileBy.XPATH, "//div[8]/div[2]/div/button"),
    'deposit_close_button2': (MobileBy.XPATH, "//button[@id='cash-close-btn']"),
    'deposit_close2_button2': (MobileBy.XPATH, "//button[2][@class='cash__action-link']"),
    'game_select': (MobileBy.XPATH, "//*[@class='games-list__game']"),
    'game_start_button': (MobileBy.XPATH, "//button[@id='GameItem.play-big-catch-bonanza-netgame']"),
    'game_start': (MobileBy.XPATH, "//*[@id='main-game-frame']")
}

'''Functions'''


def generate_random_email(length=10):
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    email = f"{random_string}@example.com"
    return email


class MyApplication:
    def __init__(self, driver):
        self.driver = driver

    def scroll_to_element(self, locator):
        element = self.find_element(locator)
        if element:
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
        else:
            logging.error(f"Element with locator '{locator}' not found.")

    def wait_for_element(self, locator, wait_time=10):
        return WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(LOCATORS[locator]))

    def find_element(self, locator):
        try:
            return self.wait_for_element(locator)
        except NoSuchElementException:
            logging.error(f"Element with locator '{locator}' not found.")
            return None

    def click_element(self, locator):
        element = self.find_element(locator)
        if element is not None:
            element.click()
            logging.info(f"Clicked element with locator '{locator}'.")

    def send_keys_to_element(self, locator, keys):
        element = self.find_element(locator)
        if element is not None:
            element.send_keys(keys)
            logging.info(f"Sent keys '{keys}' to element with locator '{locator}'.")

    def start_app(self):
        self.click_element('webview_button')
        webview = self.driver.contexts[-1]
        self.driver.switch_to.context(webview)

    def register_user(self):
        self.click_element('register_button')
        self.click_element('email_registration_tab')
        email = generate_random_email()
        self.send_keys_to_element('email_input_field', email)
        self.send_keys_to_element('password_input_field', "Qwerty123")
        self.click_element('register_submit_button')

    def handle_popups(self):
        self.click_element('deposit_pop_up_close_button')
        self.click_element('deposit_close_button2')
        self.click_element('deposit_close2_button2')

    def start_game(self):
        self.scroll_to_element('game_select')
        self.click_element('game_select')
        self.click_element('game_start_button')

    def verify_site_is_loaded(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.title_contains('Онлайн казино СлотоКінг - номер 1 в Україні')
            )
            logging.info("Site loaded successfully.")
            return True
        except TimeoutException:
            logging.error("Site is not loaded: Desired title not found within the specified wait time.")
            return False

    def verify_user_registered(self):
        try:
            deposit_button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(LOCATORS['deposit_button'])
            )
            if deposit_button:
                logging.info("User registered successfully.")
                return True
            else:
                logging.error("Failed to register user.")
                return False
        except TimeoutException:
            logging.error("Failed to register user: deposit button not found within the specified wait time.")
            return False

    def verify_game_started(self):
        try:
            game_start = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(LOCATORS['game_start'])
            )
            if game_start:
                logging.info("Game started successfully.")
                return True
            else:
                logging.error("Failed to start game.")
                return False
        except TimeoutException:
            logging.error("Failed to start game: element not found within the specified wait time.")
            return False


'''Test Case'''

MAX_RETRY_COUNT = 0


def main(retry_count=0):
    driver = None
    try:
        driver = webdriver.Remote("http://0.0.0.0:4723", desired_caps)
        driver.start_recording_screen()

        app = MyApplication(driver)
        app.start_app()
        app.verify_site_is_loaded()
        app.register_user()
        app.verify_user_registered()
        app.handle_popups()
        app.start_game()
        app.verify_game_started()

    except (WebDriverException, requests.exceptions.RequestException) as e:
        logging.error(f"Error occurred: {e}")
        if retry_count < MAX_RETRY_COUNT:
            time.sleep(10)
            main(retry_count + 1)
        else:
            logging.error("Maximum retry count exceeded. Stopping the program.")

    finally:
        if driver is not None:
            screen_recording = driver.stop_recording_screen()
            with open("slotoking_screen_recording.mp4", "wb") as out_file:
                out_file.write(base64.b64decode(screen_recording))
            driver.quit()


if __name__ == "__main__":
    main()
