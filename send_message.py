import random
import time
import pandas as pd
import undetected_chromedriver as uc
from enter_details import fill_contact_form
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    """Initialize and return a configured undetected Chrome WebDriver."""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")

    # Match your local Chrome version (131)
    driver = uc.Chrome(options=options, version_main=131)
    return driver


def main():
    # Step 1: Load the Excel file containing the saved profiles
    excel_filename = "profile_cards_pages_158_to_159.xlsx"

    try:
        print(f"Loading data from '{excel_filename}'...")
        df = pd.read_excel(excel_filename)
    except FileNotFoundError:
        print(
            f"Error: '{excel_filename}' not found. Please make sure it's in the same directory."
        )
        return

    if df.empty:
        print("The Excel file is empty.")
        return

    # Get the first row's data as a test
    first_row = df.iloc[0]
    profile_name = first_row.get("Profile Name", "Unknown")
    target_url = first_row.get("Profile URL", "N/A")

    if target_url == "N/A" or not target_url:
        print("Error: The first row does not contain a valid profile URL.")
        return

    # Step 2: Initialize the browser
    print("Initializing browser...")
    driver = setup_driver()

    try:
        # Step 3: Open the first profile URL
        print(f"\nOpening first profile for: {profile_name}")
        print(f"Navigating to: {target_url}")
        driver.get(target_url)

        # Step 4: Wait for 5 to 10 seconds after opening the page
        initial_wait = random.uniform(5, 10)
        print(
            f"Waiting for {initial_wait:.2f} seconds after opening the page..."
        )
        time.sleep(initial_wait)

        # Step 5: Check for and click the "Reject All" button if present
        print("Checking for 'Reject All' cookie button...")
        try:
            reject_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.ID, "truste-consent-required")
                )
            )
            reject_button.click()
            print("Successfully clicked 'Reject All'.")
        except Exception:
            print("'Reject All' button not found. Continuing...")

        # Step 6: Wait for another 5 to 10 seconds
        second_wait = random.uniform(5, 10)
        print(f"Waiting for another {second_wait:.2f} seconds...")
        time.sleep(second_wait)

        # Step 7: Click the "Contact partner" button
        print("Looking for 'Contact partner' button...")
        contact_button_xpath = (
            '//udex-button[contains(., "Contact partner")]'
        )

        try:
            contact_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, contact_button_xpath))
            )
            contact_button.click()
            print("Successfully clicked 'Contact partner'.")

            # Step 8: Call the form filler function from enter_details.py
            time.sleep(2)  # Short pause for the form container to slide/pop up
            fill_contact_form(driver)

        except Exception as e:
            print(f"Could not find or click 'Contact partner' button: {e}")

        # Pause here so you can verify the filled form
        print(
            "\n[Paused] Form has been filled. Review it in the browser window."
        )
        input("Press Enter to close the browser...")

    finally:
        # Step 9: Clean up and close the browser
        driver.quit()


if __name__ == "__main__":
    main()