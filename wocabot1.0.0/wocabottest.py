import time
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to load answers from JSON file
def load_answers(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Function to start automation
def start_automation():
    global driver, correct_answers

    # Get JSON file path from user selection
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not file_path:
        messagebox.showerror("Error", "No file selected!")
        return

    try:
        correct_answers = load_answers(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load JSON: {e}")
        return

    # Setup Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    # Open WocaBee
    URL = "https://wocabee.app"
    driver.get(URL)
    time.sleep(5)  # Allow page to load

    messagebox.showinfo("Login Required", "Log in to WocaBee manually and then click OK to continue.")

    # Run automation in a separate thread
    threading.Thread(target=automation_loop, daemon=True).start()

# Function to safely find elements
def find_element_safe(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except Exception:
        return None

# Function to check if an overlay is present
def is_overlay_present(driver):
    try:
        overlay = driver.find_element(By.XPATH, "//div[contains(@class, 'overlay')]")
        return overlay.is_displayed()
    except Exception:
        return False

# Main automation loop
def automation_loop():
    global driver, correct_answers

    while True:
        try:
            question_element = find_element_safe(driver, By.XPATH, "//span[contains(@id, 'q_word')]")
            if not question_element:
                print("⚠ No more questions found. Exiting.")
                break

            question_text = question_element.get_attribute("innerText").strip().lower()
            print(f"🔍 Detected Word: {question_text}")

            if question_text in correct_answers:
                answer = correct_answers[question_text]

                # Find input field
                input_field = find_element_safe(driver, By.XPATH, "//input[contains(@id, 'translateFallingWordAnswer')]")
                if input_field:
                    if is_overlay_present(driver):
                        WebDriverWait(driver, 20).until(lambda driver: not is_overlay_present(driver))

                    actions = ActionChains(driver)
                    actions.click(input_field)
                    actions.send_keys(answer)
                    actions.perform()
                    print(f"✅ Answered: {answer}")
                else:
                    print("❌ Input field not found. Skipping...")
                    continue

                # Click the check button
                check_button = find_element_safe(driver, By.XPATH, "//button[contains(@id, 'translateFallingWordSubmitBtn')]")
                if check_button:
                    check_button.click()
                    print("🖱 Clicked Check Button")
                else:
                    print("❌ Check button not found.")

                time.sleep(3)

            else:
                print("⚠ Word not found in dictionary. Stopping.")
                break

        except Exception as e:
            print(f"❌ Error: {e}")
            break

    messagebox.showinfo("Done", "Automation complete!")
    driver.quit()

# Create GUI
root = tk.Tk()
root.title("WocaBee AutoSolver")
root.geometry("300x150")

start_button = tk.Button(root, text="Start Automation", command=start_automation, font=("Arial", 12))
start_button.pack(pady=20)

root.mainloop()
