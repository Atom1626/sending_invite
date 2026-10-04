import random
import time
import re
import pandas as pd
import undetected_chromedriver as uc
from enter_details import fill_contact_form
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from helper_utils import random_wait, get_installed_chrome_major_version

def clean_company_name(name):
    """Cleans company name by removing 'Profile Card:' prefix, all spaces, and lowercasing."""
    if pd.isna(name):
        return ""
    
    name_str = str(name).strip()
    # Remove 'Profile Card:' prefix (case-insensitive)
    name_str = re.sub(r'(?i)^profile\s*card\s*:\s*', '', name_str)
    # Remove all whitespace and convert to lowercase
    name_str = re.sub(r'\s+', '', name_str).lower()
    
    return name_str


def setup_driver():
    """Initialize and return a configured undetected Chrome WebDriver with auto Chrome version detection."""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")

    major_v = get_installed_chrome_major_version()
    if major_v:
        driver = uc.Chrome(options=options, version_main=major_v)
    else:
        try:
            driver = uc.Chrome(options=options)
        except Exception:
            driver = uc.Chrome()
    return driver


def run_send_messages(from_page=158, to_page=159, details=None, client_excel_filename="ClientNames.xlsx", log_func=print, stop_event=None, excel_override=None, auto_close=True):
    """Sends contact messages to target profiles loaded from Excel."""
    if not details:
        log_func("Error: No contact details provided from UI. Please fill out form details in the GUI before sending invites.")
        return

    if excel_override:
        excel_filename = excel_override
    else:
        excel_filename = f"profile_cards_pages_{from_page}_to_{to_page}.xlsx"

    # --- 1. Load Existing Client Data ---
    existing_clients = set()
    try:
        log_func(f"Loading client list from '{client_excel_filename}'...")
        client_df = pd.read_excel(client_excel_filename)
        
        if "Client Names" in client_df.columns:
            # Clean each client name and store in a Set for super-fast lookups
            raw_clients = client_df["Client Names"].tolist()
            existing_clients = {clean_company_name(name) for name in raw_clients if str(name).strip()}
            log_func(f"Loaded {len(existing_clients)} unique existing clients for comparison.")
        else:
            log_func(f"Warning: 'Client Names' column not found in '{client_excel_filename}'. Skipping client check.")
    except FileNotFoundError:
        log_func(f"Warning: '{client_excel_filename}' not found. Skipping existing client check.")


    # --- 2. Load Target Profiles Data ---
    try:
        log_func(f"Loading target profiles from '{excel_filename}'...")
        df = pd.read_excel(excel_filename)
    except FileNotFoundError:
        log_func(f"Error: Target Excel file '{excel_filename}' not found. Please ensure link extraction has been run for pages {from_page} to {to_page}.")
        return

    if df.empty:
        log_func(f"Error: The target Excel file '{excel_filename}' is empty.")
        return

    # Ensure the needed columns exist
    if "sent status" not in df.columns:
        df["sent status"] = ""
    if "status message" not in df.columns:
        df["status message"] = ""

    log_func("Initializing browser...")
    driver = setup_driver()

    try:
        for index, row in df.iterrows():
            if stop_event and stop_event.is_set():
                log_func("[CANCELLED] Sending invites process stopped by user.")
                break

            profile_name = row.get("Profile Name", "Unknown")
            target_url = row.get("Profile URL", "N/A")
            
            raw_status = row.get("sent status", "")
            if pd.isna(raw_status):
                status_clean = ""
            else:
                status_clean = str(raw_status).strip().lower()

            # A. Skip if already processed in a previous run
            if status_clean in ["success", "failed", "already our client"]:
                log_func(f"Skipping {profile_name} - already processed with status: '{raw_status}'.")
                continue

            # B. Check if they are an existing client
            cleaned_profile = clean_company_name(profile_name)
            if cleaned_profile in existing_clients:
                log_func(f"Skipping {profile_name} - MATCHED existing client in '{client_excel_filename}'.")
                df.at[index, "sent status"] = "already our client"
                df.at[index, "status message"] = "Skipped: Client match found"
                df.to_excel(excel_filename, index=False)
                continue

            # C. Check if URL is missing
            if target_url == "N/A" or pd.isna(target_url):
                log_func(f"Skipping row {index + 1}: No valid URL.")
                continue

            # --- Proceed with Automation ---
            log_func(f"\n--- Processing Row {index + 1}/{len(df)}: {profile_name} ---")
            log_func(f"Navigating to: {target_url}")
            driver.get(target_url)

            initial_wait = random.uniform(5, 8)
            time.sleep(initial_wait)

            if stop_event and stop_event.is_set():
                log_func("[CANCELLED] Process stopped by user.")
                break

            log_func("Checking for 'Reject All' cookie button...")
            try:
                reject_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "truste-consent-required"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reject_button)
                reject_button.click()
                log_func("Successfully clicked 'Reject All'.")
                time.sleep(2)  
            except Exception:
                log_func("'Reject All' button not found on this page. Continuing...")

            time.sleep(random.uniform(2, 4))

            if stop_event and stop_event.is_set():
                log_func("[CANCELLED] Process stopped by user.")
                break

            log_func("Looking for 'Contact partner' button...")
            contact_button_xpath = '//udex-button[contains(., "Contact partner")]'

            try:
                contact_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, contact_button_xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contact_button)
                contact_button.click()
                log_func("Successfully clicked 'Contact partner'.")

                random_wait()
                
                # Execute form filling logic - unpack both returned values
                status, status_msg = fill_contact_form(driver, details=details)

                # TRIGGER STOP EXECUTION IF REQUIRED
                if status == "stop_execution":
                    log_func(f"\n[HALTED] Script stopped at Row {index + 1} due to missing 'Close' button.")
                    break

                # Save both status and the extracted message to the dataframe
                df.at[index, "sent status"] = status
                if status_msg:
                    df.at[index, "status message"] = status_msg
                    
                log_func(f"Recorded status: {status} | Message: {status_msg}")

            except Exception as e:
                log_func(f"Could not interact with profile {profile_name}: {e}")
                df.at[index, "sent status"] = "failed"

            # Save progress to Excel immediately
            df.to_excel(excel_filename, index=False)
            log_func(f"Saved progress to '{excel_filename}'.")

    finally:
        log_func("\nAutomation loop finished. Closing browser session.")
        driver.quit()


def main():
    run_send_messages(158, 159, auto_close=False)


if __name__ == "__main__":
    main()