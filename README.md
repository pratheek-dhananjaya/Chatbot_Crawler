# Web Chatbot Detector

Our research over the last several weeks has been on the **automated identification and verification of AI-powered chatbots embedded within websites**, especially those that integrate large language models (LLMs) like Claude from Anthropic, GPT from OpenAI, or Gemini from Google. We started by investigating the common ways that chatbots are incorporated into online applications, ranging from proprietary in-house solutions to outside suppliers like Intercom, Zendesk, and Botpress. By examining browser network traffic, loaded JavaScript files, DOM structures, and cookie consent exchanges, we were able to find _hard evidence_ of chatbot presence. To retrieve JavaScript resources even when they are obfuscated, we developed a hybrid process that combines DOM scraping, OCR, Chrome DevTools Protocol inspection, and keyword and regex-based pattern identification. In order to prove the use of AI chat systems, we applied four layers of evidence-gathering, from traffic logs to physical UI inspection, to validate our framework across well-known websites like `messengerbot.app`. Our efforts ultimately result in an automated technique that can detect chatbots on a big scale with little assistance from humans, setting the stage for scalable audits of LLM deployments online.

This project detects the presence of AI-powered chatbots or third-party live chat support on a list of websites by analyzing their network activity. It leverages SeleniumWire to capture HTTP(S) traffic, applies pattern matching for known chatbot libraries or LLM providers, and saves the detection results for further analysis.

—--

Features:

- Visits websites and collects all HTTP(S) requests.
- Detects chatbots using:
  - **Keyword-based detection** (e.g., openai, gemini, huggingface, etc.)
  - **Regex-based pattern matching** for known vendors (e.g., Intercom, Zendesk, Tidio, Dialogflow).
- Automatically clicks cookie consent banners (accept, agree, allow, etc.).
- Saves a `.json` file of all network logs per website.
- Runs in parallel using Python's `ThreadPoolExecutor`.
- Outputs results in a CSV summary.

---

## Input Format

Provide a file named `websites.csv` in the root directory with one website per line.

—--

## Requirements

pip3 install selenium selenium-wire pandas
