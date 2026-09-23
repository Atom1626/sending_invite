import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def fill_contact_form(driver):
    """Fills out the contact form by safely piercing shadow DOMs for custom dropdowns."""

    # --- DEFINE YOUR DETAILS HERE ---
    details = {
        "firstName": "Kiran",
        "lastName": "K",
        "email": "kiran@globalwavesoftech.com",
        "phone": "+91 970144 4296",
        "company": "Globalwave Softech",
        "country": "India",
        "relationship": "Prospective Customer",
        # Write your multi-line message naturally using triple quotes below:
        "message": """Sub: SAP Services & Staffing Support - Globalwave Softech

Dear Team,

Greetings from Globalwave Softech!

We are a global SAP services and staffing company with 200+ employees across the USA and India, offering expertise across various SAP modules.

We can support your upcoming requirements through:

SAP Implementation, Support Services & Migration Projects
Contract & Contract-to-Hire Staffing
Full-Time Recruitment
Experienced and immediately available SAP resources
Competitive and flexible pricing
We would be happy to connect and understand your current or upcoming SAP requirements and explore opportunities to work together.

Please share your email address and convenient time for a quick call.

You can also reach us at admin@globalwavesoftech.com or kiran@globalwavesoftech.com.

Looking forward to connecting with you.

Best Regards,
Kiran
Globalwave Softech""",
    }
    # --------------------------------


    wait = WebDriverWait(driver, 15)

    try:
        print("Filling out contact form details...")
        time.sleep(2)  # Allow the modal to fully render

        # Helper for standard text inputs (First name, Last name, etc.)
        def set_text_field(name_attr, value):
            try:
                element = wait.until(
                    EC.presence_of_element_located((By.NAME, name_attr))
                )
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
                driver.execute_script("arguments[0].value = arguments[1];", element, value)
                driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                    "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                    element
                )
            except Exception as ex:
                print(f"Warning: Could not fill field '{name_attr}': {ex}")

        # 1 to 5: Standard Fields
        set_text_field("firstName", details["firstName"])
        set_text_field("lastName", details["lastName"])
        set_text_field("email", details["email"])
        set_text_field("phone", details["phone"])
        set_text_field("company", details["company"])

# 6. Country Selection 
        print("Selecting country...")
        try:
            # Open the dropdown
            driver.execute_script("""
                const host = document.querySelector('udex-country-selector[name="country"]');
                if (host && host.shadowRoot) {
                    const trigger = host.shadowRoot.querySelector('.udex-text-field__trigger');
                    if (trigger) trigger.click();
                }
            """)
            time.sleep(1) # Wait for dropdown animation

            # Target the exact item and click its inner shadow element
            driver.execute_script("""
                const host = document.querySelector('udex-country-selector[name="country"]');
                if (host && host.shadowRoot) {
                    // Find India using its unique ID "IN"
                    const item = host.shadowRoot.querySelector('udex-list-item#IN') || 
                                 host.shadowRoot.querySelector('udex-list-item[label*="India"]');
                    
                    if (item) {
                        // Scroll the dropdown down to India so it is interactable
                        item.scrollIntoView({block: 'center'});
                        
                        // Trigger standard clicks
                        item.click();
                        item.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));
                        
                        // CRITICAL FIX: Pierce the item's own shadow DOM to click the actual hidden list tag
                        if (item.shadowRoot) {
                            const innerItem = item.shadowRoot.querySelector('li') || item.shadowRoot.firstElementChild;
                            if (innerItem) innerItem.click();
                        }
                    }
                }
            """)
        except Exception as e:
            print(f"Error selecting country: {e}")


# 7. Relationship Selection
        print("Selecting relationship...")
        try:
            # Open the dropdown
            driver.execute_script("""
                const host = document.querySelector('udex-select-box[name="relationship"]');
                if (host && host.shadowRoot) {
                    const trigger = host.shadowRoot.querySelector('.udex-text-field__trigger');
                    if (trigger) trigger.click();
                }
            """)
            time.sleep(1)

            # Target the exact item (udex-list-item) inside the shadow DOM
            driver.execute_script("""
                const host = document.querySelector('udex-select-box[name="relationship"]');
                if (host && host.shadowRoot) {
                    // Using the correct tag name found in the live DOM
                    const item = host.shadowRoot.querySelector('udex-list-item[label="Prospective Customer"]');
                    
                    if (item) {
                        item.scrollIntoView({block: 'center'});
                        
                        // Trigger standard clicks
                        item.click();
                        item.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));
                        
                        // Pierce the item's own shadow DOM just like the country field
                        if (item.shadowRoot) {
                            const innerItem = item.shadowRoot.querySelector('li') || item.shadowRoot.firstElementChild;
                            if (innerItem) innerItem.click();
                        }
                    }
                }
            """)
        except Exception as e:
            print(f"Error selecting relationship: {e}")

        # 8. Message Textarea
        try:
            msg_element = wait.until(
                EC.presence_of_element_located((By.NAME, "message"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", msg_element)
            driver.execute_script("arguments[0].value = arguments[1];", msg_element, details["message"])
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                msg_element
            )
            print("Successfully filled message field.")
        except Exception as ex:
            print(f"Warning: Could not fill message field: {ex}")

        print("Successfully processed all form fields.")

# 9. Agreement Checkbox
        print("Clicking agreement checkbox...")
        try:
            # We use a script to find the checkbox, handling both Light and Shadow DOM possibilities
            driver.execute_script("""
                // Try finding the custom element tag first
                let checkboxHost = document.querySelector('udex-checkbox') || document.querySelector('ui5-checkbox');
                
                if (checkboxHost) {
                    checkboxHost.scrollIntoView({block: 'center'});
                    
                    // Click the host component
                    checkboxHost.click();
                    checkboxHost.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));
                    
                    // Also pierce the shadow DOM to click the inner box specifically
                    if (checkboxHost.shadowRoot) {
                        const innerBox = checkboxHost.shadowRoot.querySelector('.ui5-checkbox-inner');
                        if (innerBox) {
                            innerBox.click();
                        }
                    }
                } else {
                    // Fallback if the inner checkbox class is just sitting in the normal DOM
                    let innerDom = document.querySelector('.ui5-checkbox-inner');
                    if (innerDom) {
                        innerDom.scrollIntoView({block: 'center'});
                        innerDom.click();
                    }
                }
            """)
            print("Successfully clicked the agreement checkbox.")
        except Exception as e:
            print(f"Error clicking agreement checkbox: {e}")

        print("Successfully processed all form fields.")
        
 # 10. Click reCAPTCHA Checkbox
        print("Handling reCAPTCHA...")
        try:
            # Wait for the reCAPTCHA iframe to appear and switch driver focus to it
            recaptcha_iframe = wait.until(
                EC.presence_of_element_located((By.XPATH, '//iframe[contains(@src, "recaptcha")]'))
            )
            driver.switch_to.frame(recaptcha_iframe)
            
            # Now wait for the checkbox inside the iframe and click it
            recaptcha_checkbox = wait.until(
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", recaptcha_checkbox)
            time.sleep(0.5)  # Brief pause to look slightly more human
            recaptcha_checkbox.click()
            print("Successfully clicked the reCAPTCHA checkbox.")
            
            # Switch back to the main page content so the script can continue normally
            driver.switch_to.default_content()
            time.sleep(2)  # Give the reCAPTCHA a moment to process the click
            
        except Exception as e:
            print(f"Error handling reCAPTCHA: {e}")
            # Ensure we switch back to the main page even if it fails
            driver.switch_to.default_content()

        print("Successfully processed all form fields.")
        return True

    except Exception as e:
        print(f"An error occurred while filling the form: {e}")
        return False