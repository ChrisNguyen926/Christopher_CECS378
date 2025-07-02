# agentic_ai_lab_firecrawl.py
# Agentic AI Lab: Firecrawl API → Offline LLM → PDF Generator

import ollama
import requests
from fpdf import FPDF

# ======== CONFIGURATION ========
FIRECRAWL_API_KEY = 'fc-2c14c8ade5234f55b60e4120d59bb352'   # ← replace with your key
FIRECRAWL_URL     = 'https://api.firecrawl.dev/v1/scrape'
MODEL_NAME        = 'mistral:7b'                    # ← adjust to a model you’ve pulled

# ======== DATA COLLECTION FROM WEB ========
def collect_data_from_url(url: str) -> str:
    headers = {
        'Authorization': f'Bearer {FIRECRAWL_API_KEY}',
        'Content-Type':  'application/json',
    }
    payload = {
        'url':             url,
        'onlyMainContent': False,            # set True if you want just the article body
        'formats':         ['markdown'],     # get back Markdown text
    }

    resp = requests.post(FIRECRAWL_URL, headers=headers, json=payload)
    if resp.status_code != 200:
        # print full error for debugging
        print("Firecrawl error:", resp.status_code, resp.text)
        resp.raise_for_status()

    body = resp.json()
    # v1 returns {"success": true, "data": { "markdown": "…", … }}
    return body['data']['markdown']

# ======== PROCESS USING OFFLINE LLM ========
def process_with_llm(content: str) -> str:
    print("\nProcessing content with offline LLM…")
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{
            'role': 'user',
            'content': (
                "Please summarize and extract key actionable insights from the following "
                f"content for a cybersecurity student:\n\n{content}"
            )
        }]
    )
    return response['message']['content']

# ======== GENERATE PDF REPORT ========
def generate_pdf(content: str, filename: str = "agentic_ai_summary.pdf") -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    print(f"PDF report generated: {filename}")

# ======== MAIN EXECUTION FLOW ========
def main():
    print("=== Agentic AI Lab: Firecrawl + Offline LLM + PDF Generator ===")
    url = input("Enter the URL to collect data from: ")

    try:
        scraped_markdown = collect_data_from_url(url)
        if not scraped_markdown:
            print("⚠️  No content retrieved from the URL.")
            return

        print("\n--- Scraped Content (Markdown Preview) ---")
        print(scraped_markdown[:500] + "\n…")  # preview first 500 chars

        summary = process_with_llm(scraped_markdown)
        print("\n--- LLM Processed Summary ---")
        print(summary)

        generate_pdf(summary)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
