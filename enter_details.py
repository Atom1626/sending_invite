import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from helper_utils import random_wait

def fill_contact_form(driver):
    """Fills out the contact form, handles dropdowns, reCAPTCHA, and verifies final success."""


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
        random_wait()  

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
        random_wait()
        set_text_field("lastName", details["lastName"])
        random_wait()
        set_text_field("email", details["email"])
        random_wait()
        set_text_field("phone", details["phone"])
        random_wait()
        set_text_field("company", details["company"])
        random_wait()

        # 6. Country Selection 
        print("Selecting country...")
        try:
            driver.execute_script("""
                const host = document.querySelector('udex-country-selector[name="country"]');
                if (host && host.shadowRoot) {
                    const trigger = host.shadowRoot.querySelector('.udex-text-field__trigger');
                    if (trigger) trigger.click();
                }
            """)
            time.sleep(1)

            driver.execute_script("""
                const host = document.querySelector('udex-country-selector[name="country"]');
                if (host && host.shadowRoot) {
                    const item = host.shadowRoot.querySelector('udex-list-item#IN') || 
                                 host.shadowRoot.querySelector('udex-list-item[label*="India"]');
                    
                    if (item) {
                        item.scrollIntoView({block: 'center'});
                        item.click();
                        item.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));
                        
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
            driver.execute_script("""
                const host = document.querySelector('udex-select-box[name="relationship"]');
                if (host && host.shadowRoot) {
                    const trigger = host.shadowRoot.querySelector('.udex-text-field__trigger');
                    if (trigger) trigger.click();
                }
            """)
            time.sleep(1)

            driver.execute_script("""
                const host = document.querySelector('udex-select-box[name="relationship"]');
                if (host && host.shadowRoot) {
                    const item = host.shadowRoot.querySelector('udex-list-item[label="Prospective Customer"]');
                    
                    if (item) {
                        item.scrollIntoView({block: 'center'});
                        item.click();
                        item.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));
                        
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

        random_wait()
        # 9. Agreement Checkbox
        print("Clicking agreement checkbox...")
        try:
            driver.execute_script("""
                let checkboxHost = document.querySelector('udex-checkbox') || document.querySelector('ui5-checkbox');
                if (checkboxHost) {
                    checkboxHost.scrollIntoView({block: 'center'});
                    checkboxHost.click();
                    checkboxHost.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));
                    
                    if (checkboxHost.shadowRoot) {
                        const innerBox = checkboxHost.shadowRoot.querySelector('.ui5-checkbox-inner');
                        if (innerBox) innerBox.click();
                    }
                } else {
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

        random_wait()
        # 10. Click reCAPTCHA Checkbox
        print("Handling reCAPTCHA...")
        try:
            recaptcha_iframe = wait.until(
                EC.presence_of_element_located((By.XPATH, '//iframe[contains(@src, "recaptcha")]'))
            )
            driver.switch_to.frame(recaptcha_iframe)
            
            recaptcha_checkbox = wait.until(
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", recaptcha_checkbox)
            time.sleep(1) 
            recaptcha_checkbox.click()
            
            # Wait for green checkmark (aria-checked becomes "true")
            print("Waiting for reCAPTCHA verification...")
            verified = False
            start_time = time.time()
            
            while time.time() - start_time < 60:
                is_checked = recaptcha_checkbox.get_attribute("aria-checked")
                if is_checked == "true":
                    verified = True
                    print("reCAPTCHA verified successfully!")
                    break
                
                if int(time.time() - start_time) % 10 == 0:
                    print("Please solve the image puzzle on the screen...")
                
                time.sleep(1)
            
            driver.switch_to.default_content()
            random_wait() 
            
            if not verified:
                print("Failed: reCAPTCHA was not solved within 60 seconds.")
                return "failed", ""
            
        except Exception as e:
            print(f"Error handling reCAPTCHA: {e}")
            driver.switch_to.default_content()
            return "failed", ""

        # 11. Click Send Button
        print("Waiting for Send button to become enabled and clicking it...")
        send_start_time = time.time()
        clicked_send = False
        
        while time.time() - send_start_time < 15: 
            js_result = driver.execute_script("""
                let sendBtnHost = Array.from(document.querySelectorAll('udex-button, ui5-button')).find(
                    btn => (btn.textContent && btn.textContent.trim() === 'Send') || 
                           btn.getAttribute('aria-label') === 'Send' ||
                           btn.classList.contains('lead-form-modal__submit')
                );
                
                if (sendBtnHost) {
                    if (sendBtnHost.disabled || sendBtnHost.hasAttribute('disabled') && sendBtnHost.getAttribute('disabled') !== 'false') {
                        return "disabled";
                    }
                    sendBtnHost.scrollIntoView({block: 'center'});
                    sendBtnHost.click();
                    
                    if (sendBtnHost.shadowRoot) {
                        let innerBtn = sendBtnHost.shadowRoot.querySelector('button');
                        if (innerBtn) innerBtn.click();
                    }
                    return "clicked";
                }
                return "not_found";
            """)
            
            if js_result == "clicked":
                clicked_send = True
                print("Successfully verified and clicked the Send button.")
                break
            elif js_result == "disabled":
                print("Send button is still disabled (waiting for form/reCAPTCHA validation)...")
            
            time.sleep(1.5)
            
        if not clicked_send:
            print("Failed: Send button never became enabled or was not found.")
            return "failed", ""

        # 12. Explicitly wait for "Contact Request Sent", grab message, WAIT 10 SECONDS, then click Close
        print("Waiting for 'Contact Request Sent' message...")
        start_time = time.time()
        
        while time.time() - start_time < 30: 
            # We now return a dictionary with the status and the extracted message
            js_result = driver.execute_script("""
                let successTitle = document.querySelector('.lead-form-modal__indicator-title');
                let successSubtitle = document.querySelector('.lead-form-modal__indicator-subtitle');
                let isSuccess = successTitle && successTitle.textContent.includes('Contact Request Sent');
                
                if (isSuccess) {
                    let closeBtn = Array.from(document.querySelectorAll('udex-button, ui5-button')).find(
                        b => b.textContent && b.textContent.trim() === 'Close'
                    );
                    
                    if (closeBtn) {
                        let msg = successSubtitle ? successSubtitle.textContent.trim() : "Request submitted successfully.";
                        return { "status": "ready_to_close", "message": msg };
                    }
                    return { "status": "success_but_no_close", "message": "" };
                }
                return { "status": "waiting", "message": "" };
            """)
            
            js_status = js_result.get("status")
            js_message = js_result.get("message")
            
            if js_status == "ready_to_close":
                print(f"Success message detected: '{js_message}'")
                print("Waiting 10 seconds before clicking Close...")
                random_wait()  # Waiting 10 seconds BEFORE clicking close
                
                # Now actually click the Close button
                driver.execute_script("""
                    let closeBtn = Array.from(document.querySelectorAll('udex-button, ui5-button')).find(
                        b => b.textContent && b.textContent.trim() === 'Close'
                    );
                    if (closeBtn) {
                        closeBtn.scrollIntoView({block: 'center'});
                        closeBtn.click();
                        
                        if (closeBtn.shadowRoot) {
                            let innerBtn = closeBtn.shadowRoot.querySelector('button');
                            if (innerBtn) innerBtn.click();
                        }
                    }
                """)
                print("'Close' button clicked!")
                return "success", js_message
                
            elif js_status == "success_but_no_close":
                print("Found success text, but no Close button yet. Retrying...")
            
            time.sleep(1.5)

        # If it reaches here, the 30 seconds expired without successfully closing the window
        print("\n[FATAL ERROR] 'Close' button or success message not found within 30 seconds.")
        return "stop_execution", ""

    except Exception as e:
        print(f"An error occurred while filling the form: {e}")
        return "failed", ""