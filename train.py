from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import openai
import re
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
load_dotenv()
app = Flask(__name__)

# Retrieve the OpenAI API key from .env
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("The OpenAI API key is missing.")
openai.api_key = api_key

# Clean HTML content by removing unnecessary tags
def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["meta", "link", "noscript", "style", "script"]):
        tag.decompose()
    return str(soup)

# Truncate HTML content to a fixed token limit
def truncate_html_to_fixed_limit(html_content):
    fixed_limit = 15000
    truncated_html = html_content[:fixed_limit]
    closing_index = truncated_html.rfind("</")
    if closing_index != -1:
        truncated_html = truncated_html[:closing_index] + "</>"
    return truncated_html

# Get dynamic CSS selectors using OpenAI
def get_dynamic_selectors(html_content):
    cleaned_html = clean_html(html_content)
    truncated_html = truncate_html_to_fixed_limit(cleaned_html)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in analyzing HTML content and extracting CSS selectors."},
            {"role": "user", "content": f"Analyze the following HTML and identify the CSS selectors for product reviews, including title, body, rating, and reviewer:\n{truncated_html}"}
        ],
        max_tokens=150,
        temperature=0.7
    )
    response_content = response.choices[0].message['content'].strip()
    print("OpenAI Response:", response_content)  # Debugging output
    return response_content

# Safely extract regex matches
def safe_extract(pattern, text):
    match = re.search(pattern, text)
    return match.group(1) if match else None

# Extract reviews from a single page
def extract_reviews(page, selectors):
    reviews = []
    try:
        titles = page.query_selector_all(selectors['title']) or []
        bodies = page.query_selector_all(selectors['body']) or []
        ratings = page.query_selector_all(selectors['rating']) or []
        reviewers = page.query_selector_all(selectors['reviewer']) or []

        for i in range(min(len(titles), len(bodies), len(ratings), len(reviewers))):
            try:
                reviews.append({
                    "title": titles[i].inner_text().strip() if titles[i] else "N/A",
                    "body": bodies[i].inner_text().strip() if bodies[i] else "N/A",
                    "rating": int(ratings[i].inner_text().strip()) if ratings[i] else None,
                    "reviewer": reviewers[i].inner_text().strip() if reviewers[i] else "N/A",
                })
            except Exception as e:
                print(f"Error extracting a single review: {e}")
    except Exception as e:
        print(f"Error extracting reviews: {e}")
    return reviews

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Please provide a URL."}), 400

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)

        html_content = page.content()

        try:
            selectors_response = get_dynamic_selectors(html_content)
            print("Selectors Response:", selectors_response)
        except Exception as e:
            print(f"Error generating selectors: {e}")
            return jsonify({"error": "Failed to generate selectors using OpenAI."}), 500

        selectors = {
            "title": safe_extract(r'title:\s*(.+)', selectors_response) or "h2.review-title",
            "body": safe_extract(r'body:\s*(.+)', selectors_response) or "div.review-body",
            "rating": safe_extract(r'rating:\s*(.+)', selectors_response) or "span.review-rating",
            "reviewer": safe_extract(r'reviewer:\s*(.+)', selectors_response) or "span.reviewer-name",
        }

        missing_selectors = [key for key, value in selectors.items() if not value]
        if missing_selectors:
            print(f"Missing selectors: {missing_selectors}")
            return jsonify({"error": f"Failed to extract all selectors. Missing: {missing_selectors}"}), 500

        all_reviews = []
        while True:
            reviews = extract_reviews(page, selectors)
            all_reviews.extend(reviews)

            try:
                next_button = page.query_selector("button.next, a.next, div.pagination-next")
                if next_button and next_button.is_visible():
                    next_button.click()
                    page.wait_for_timeout(2000)
                else:
                    break
            except Exception as e:
                print(f"Error navigating to the next page: {e}")
                break

        browser.close()

    return jsonify({"reviews_count": len(all_reviews), "reviews": all_reviews})

if __name__ == '__main__':
    app.run(debug=True)