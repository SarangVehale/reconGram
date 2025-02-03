from playwright.sync_api import sync_playwright
import time
import random

def random_delay(min_seconds=1, max_seconds=3):
    """Random delay to simulate human typing and interactions."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def human_type(page, selector, text, min_typing_delay=0.1, max_typing_delay=0.3):
    """Simulate typing in a human-like way by typing each character with a delay."""
    for char in text:
        page.type(selector, char)
        random_delay(min_seconds=min_typing_delay, max_seconds=max_typing_delay)

def instagram_login(user_input):
    """Simulate logging into Instagram using the provided email or mobile number."""
    if user_input.startswith("+91"):
        user_input = user_input[3:]  # Remove "+91" country code if present

    chrome_path = "/usr/bin/google-chrome"  # Set the correct path for Chrome on your system

    with sync_playwright() as p:
        # Launch browser with the specified Chrome path
        browser = p.chromium.launch(
            executable_path=chrome_path, headless=True
        )

        # Create a new browser context with a custom user agent
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.117 Safari/537.36'
        )

        # Create a new page within the context
        page = context.new_page()

        # Navigate to the Instagram reset password page
        page.goto('https://www.instagram.com/accounts/password/reset/')

        # Wait for the input field to appear
        page.wait_for_selector('input[name="cppEmailOrUsername"]')

        # Type the user input
        human_type(page, 'input[name="cppEmailOrUsername"]', user_input)

        # Add random delay before pressing Enter
        random_delay(min_seconds=1, max_seconds=2)

        # Press Enter after typing the input
        page.press('input[name="cppEmailOrUsername"]', 'Enter')

        # Add a delay to allow the page to load
        random_delay(min_seconds=2, max_seconds=3)

        # Check for elements to determine account status
        password_field = page.query_selector('input[class="r4vIwl IX3CMV"]')
        not_found_element = page.query_selector('div[class="_acb4"]')

        if password_field:
            print("Yes, Instagram Account Found!")
            result = 1
        elif not_found_element:
            error_text = not_found_element.text_content().strip()
            if "Please wait a few minutes before you try again" in error_text:
                print("Instagram Account found but can't be confirmed, please try again later.")
                result = 1
            else:
                print("No, Instagram Account Not Found!")
                result = 0
        else:
            print("Unexpected error occurred!")
            result = -1

        # Close the browser after a random delay
        random_delay(min_seconds=2, max_seconds=4)
        browser.close()

        return result

if __name__ == "__main__":
    user_input = input("Enter email or mobile number: ")
    instagram_login(user_input)

