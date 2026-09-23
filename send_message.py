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
    excel_filename = "profile_cards_pages_158_to_159.xlsx"

    try:
        print(f"Loading data from '{excel_filename}'...")
        df = pd.read_excel(excel_filename)
    except FileNotFoundError:
        print(f"Error: '{excel_filename}' not found.")
        return

    if df.empty:
        print("The Excel file is empty.")
        return

    # Ensure the needed columns exist
    if "sent status" not in df.columns:
        df["sent status"] = ""
    if "status message" not in df.columns:
        df["status message"] = ""

    print("Initializing browser...")
    driver = setup_driver()

    try:
        for index, row in df.iterrows():
            profile_name = row.get("Profile Name", "Unknown")
            target_url = row.get("Profile URL", "N/A")
            
            raw_status = row.get("sent status", "")
            if pd.isna(raw_status):
                status_clean = ""
            else:
                status_clean = str(raw_status).strip().lower()

            if status_clean in ["success", "failed"]:
                print(f"Skipping {profile_name} - already processed with status: '{raw_status}'.")
                continue

            if target_url == "N/A" or pd.isna(target_url):
                print(f"Skipping row {index + 1}: No valid URL.")
                continue

            print(f"\n--- Processing Row {index + 1}: {profile_name} ---")
            print(f"Navigating to: {target_url}")
            driver.get(target_url)

            initial_wait = random.uniform(5, 8)
            time.sleep(initial_wait)

            print("Checking for 'Reject All' cookie button...")
            try:
                reject_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "truste-consent-required"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reject_button)
                reject_button.click()
                print("Successfully clicked 'Reject All'.")
                time.sleep(2)  
            except Exception:
                print("'Reject All' button not found on this page. Continuing...")

            time.sleep(random.uniform(2, 4))

            print("Looking for 'Contact partner' button...")
            contact_button_xpath = '//udex-button[contains(., "Contact partner")]'

            try:
                contact_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, contact_button_xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contact_button)
                contact_button.click()
                print("Successfully clicked 'Contact partner'.")

                time.sleep(2)
                
                # Execute form filling logic - unpack both returned values
                status, status_msg = fill_contact_form(driver)

                # TRIGGER STOP EXECUTION IF REQUIRED
                if status == "stop_execution":
                    print(f"\n[HALTED] Script stopped at Row {index + 1} due to missing 'Close' button.")
                    break

                # Save both status and the extracted message to the dataframe
                df.at[index, "sent status"] = status
                if status_msg:
                    df.at[index, "status message"] = status_msg
                    
                print(f"Recorded status: {status} | Message: {status_msg}")

            except Exception as e:
                print(f"Could not interact with profile {profile_name}: {e}")
                df.at[index, "sent status"] = "failed"

            # Save progress to Excel immediately
            df.to_excel(excel_filename, index=False)
            print(f"Saved progress to '{excel_filename}'.")

    finally:
        # If the script stopped execution due to an error, we keep the browser open for inspection
        print("\nAutomation loop finished. You may safely close the terminal/browser.")


if __name__ == "__main__":
    main()