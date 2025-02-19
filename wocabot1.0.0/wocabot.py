import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Load predefined correct answers from the JSON file
def load_answers(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# ✅ Setup Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# ✅ Open WocaBee
URL = "https://wocabee.app"
driver.get(URL)
time.sleep(5)  # Allow time for page to load

# ✅ Wait for user login (manual step)
input("👉 Log in to WocaBee and press Enter to continue...")

# ✅ Load predefined correct answers from JSON file
correct_answers = load_answers("answers.json")

# ✅ Function to find elements safely
def find_element_safe(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except Exception as e:
        print(f"❌ Element {value} not found: {e}")
        return None

# ✅ Function to check if an overlay is present (helps in case of modals blocking input)
def is_overlay_present(driver):
    try:
        # Check for a generic overlay or modal (you can adjust the selector based on the page structure)
        overlay = driver.find_element(By.XPATH, "//div[contains(@class, 'overlay')]")
        return overlay.is_displayed()
    except Exception:
        return False

# ✅ Main loop to keep answering questions
while True:
    try:
        # ✅ Attempt to find the question element (the button element)
        question_element = find_element_safe(driver, By.XPATH, "//span[contains(@id, 'q_word')]")
        
        if not question_element:
            print("⚠ No more questions found. Exiting.")
            break

        # Add debugging to check what we're extracting
        print(f"🔍 Raw Question Element: {question_element}")

        # Try to extract the text of the question from any inner element (like span or div)
        question_text = question_element.get_attribute("innerText").strip().lower()

        if not question_text:
            print("⚠ Question text is still empty. Checking the HTML of the question element...")
            print(f"❓ HTML of Question Element: {question_element.get_attribute('outerHTML')}")

        print(f"🔍 Detected Word: {question_text}")

        # ✅ Check if word is in dictionary
        if question_text in correct_answers:
            answer = correct_answers[question_text]
            print(f"✅ Answer: {answer}")

            # ✅ Find the input field (white box)
            input_field = find_element_safe(driver, By.XPATH, "//input[contains(@id, 'translateFallingWordAnswer')]")
            
            # Ensure the input field is interactable
            if input_field:
                try:
                    # Check for overlays or modals blocking the input field
                    if is_overlay_present(driver):
                        print("❌ Overlay or modal present. Waiting for it to disappear...")
                        WebDriverWait(driver, 20).until(lambda driver: not is_overlay_present(driver))
                        print("✅ Overlay disappeared.")

                    # Scroll input field into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", input_field)

                    # Check if the input field is not disabled or readonly
                    input_field_disabled = input_field.get_attribute("disabled")
                    input_field_readonly = input_field.get_attribute("readonly")
                    if input_field_disabled:
                        print("❌ Input field is disabled.")
                        continue
                    if input_field_readonly:
                        print("❌ Input field is readonly.")
                        continue

                    # Check if the input field is visible and interactable
                    WebDriverWait(driver, 10).until(EC.visibility_of(input_field))  # Make sure it's visible
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(input_field))  # Ensure it is clickable
                    print("🔍 Input field is visible and clickable.")
                    
                    # Simulate typing the answer into the input field
                    actions = ActionChains(driver)
                    actions.click(input_field)  # Focus the input field
                    actions.send_keys(answer)  # Type the answer character by character
                    actions.perform()
                    print(f"✅ Simulated typing the answer: {answer}")
                except Exception as e:
                    print(f"❌ Could not interact with input field: {e}")
                    continue
            else:
                print("❌ Input field not found. Skipping...")
                continue

            # ✅ Find and click the blue button (Check Answer)
            check_button = find_element_safe(driver, By.XPATH, "//button[contains(@id, 'translateFallingWordSubmitBtn')]")
            
            if check_button:
                try:
                    # Wait until the check button is clickable
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(check_button))
                    check_button.click()
                    print("🖱 Clicked Check Button")
                except Exception as e:
                    print(f"❌ Could not interact with check button: {e}")

            else:
                print("❌ Check button not found.")

            # ✅ Wait before the next question appears
            time.sleep(3)

        else:
            print("⚠ Word not found in dictionary. Stopping.")
            break  # Stop the loop if the word is unknown

    except Exception as e:
        print(f"❌ Error: {e}")
        break  # Stop loop if an error occurs

# ✅ Close the browser when done
print("🎉 Done! Closing browser.")
driver.quit()
