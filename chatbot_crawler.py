import os
import csv
import json
import re
import time
import pandas as pd
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PRIMARY_KEYWORDS = ['openai', 'gemini', 'claude', 'bard', 'mistral', 'anthropic', 'bedrock',
                    'generativelanguage', 'role', 'perplexity', 'huggingface', 'open-assistant']

CHATBOT_JS_PATTERNS = [
    r"live[.\-_ \t]*chat", r"inter[.\-_ \t]*com", r"chat[.\-_ \t]*bot", r"conversation[.\-_ \t]*id",
    r"live[.\-_ \t]*agent", r"assistant", r"dialogflow", r"salesforce[.\-_ \t]*live[.\-_ \t]*agent",
    r"zendesk", r"tidio", r"chat[.\-_ \t]*widget", r"automated[.\-_ \t]*chat", r"c[.\-_ \t]*bot",
    r"sierra[.\-_ \t]*chat", r"https?://.*sierra\\.chat", r"messaging", r"asapp", r"chat",
    r"help", r"messenger", r"assistant", r"bot[.\-_ \t]*press", r"genesys", r"fresh[.\-_ \t]*chat",
    r"kommunicate", r"web[.\-_ \t]*messaging", r"kodif", r"chat[.\-_ \t]*router",
    r"wonderchat", r"conigy", r"hubspot", r"chat[.\-_ \t]*woot"
]

def process_website(url):
    print(f"Processing: {url}")
    site_name = url.split("//")[-1].replace("www.", "").replace("/", "_")
    detected = False
    reason = "error:unknown"
    driver = None

    try:
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--log-level=3')
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        driver.get(url)

        # Try to accept cookies if any
        try:
            time.sleep(3)
            buttons = driver.find_elements("tag name", "button")
            for button in buttons:
                text = button.text.strip().lower()
                if any(k in text for k in ["accept", "agree", "allow", "understand", "opt-in"]):
                    button.click()
                    print("Cookie banner accepted.")
                    break
        except Exception as cookie_error:
            print("Cookie banner not handled:", cookie_error)

        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(3)

        time.sleep(10)

        network_logs = []
        for request in driver.requests:
            if request.response:
                network_logs.append({
                    "method": request.method,
                    "url": request.url,
                    "status_code": request.response.status_code,
                    "headers": dict(request.headers),
                })

        with open(f"{site_name}_log.json", "w") as f:
            json.dump(network_logs, f, indent=2)

        for log in network_logs:
            text = json.dumps(log).lower()
            for keyword in PRIMARY_KEYWORDS:
                if keyword in text:
                    detected = True
                    reason = f"Not connected to a vendor"
                    break
            if detected:
                break

        if not detected:
            for log in network_logs:
                text = json.dumps(log).lower()
                for pattern in CHATBOT_JS_PATTERNS:
                    try:
                        if re.search(pattern, text):
                            detected = True
                            reason = f"Third Party Vendor"
                            break
                    except re.error:
                        continue
                if detected:
                    break

    except Exception as e:
        reason = f"error:{str(e).splitlines()[0]}"[:150]
    finally:
        if driver:
            driver.quit()

    return {
        "website": url,
        "chatbot_detected": "Yes" if detected else "No",
        "detection_reason": reason
    }

# Read websites from CSV
with open("websites.csv", "r") as file:
    reader = csv.reader(file)
    websites = [row[0].strip() for row in reader if row]

results = []

# Run parallel processing with 4 threads
with ThreadPoolExecutor(max_workers=4) as executor:
    future_to_url = {executor.submit(process_website, url): url for url in websites}
    for future in as_completed(future_to_url):
        try:
            result = future.result()
            results.append(result)
        except Exception as e:
            results.append({
                "website": future_to_url[future],
                "chatbot_detected": "No",
                "detection_reason": f"error:{str(e)[:150]}"
            })

# Save summary CSV
summary_file = "chatbot_detection_summary2.csv"
pd.DataFrame(results).to_csv(summary_file, index=False)
print(f"\nParallel detection complete. Summary saved to {summary_file}")
