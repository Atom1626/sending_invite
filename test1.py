import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    """Initialize and return a configured undetected Chrome WebDriver."""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")

    # Pass version_main to match your local Chrome (131)
    driver = uc.Chrome(options=options, version_main=131)
    return driver


def main():
    # Step 1: Load the URL from config.json
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            target_url = config.get("url")

        if not target_url:
            raise ValueError("The 'url' key is missing in config.json")

    except FileNotFoundError:
        print("Error: 'config.json' file not found. Please create it.")
        return
    except json.JSONDecodeError:
        print("Error: 'config.json' is not a valid JSON file.")
        return

    # Step 2: Initialize the browser
    print("Initializing browser...")
    driver = setup_driver()

    try:
        # Step 3: Open the URL
        print(f"Navigating to: {target_url}")
        driver.get(target_url)

        # Step 4: Conditionally check for and click the cookie consent button
        print("Checking for cookie consent banner...")
        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "truste-consent-button"))
            )
            accept_button.click()
            print("Successfully clicked 'I accept all cookies'.")
        except Exception:
            print("Cookie banner not found. Continuing without clicking.")

        # Pause to let you view the page afterward
        input("Press Enter to close the browser...")

    finally:
        # Step 5: Clean up and close the browser
        driver.quit()


if __name__ == "__main__":
    main()