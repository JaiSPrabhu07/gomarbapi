# Extract Product Reviews API

This project provides an API for extracting product reviews dynamically from e-commerce websites using **Playwright** and **OpenAI**. The application is built with Flask and is deployed on **Koyeb**.

## API Endpoint

**Base URL:**
```
https://thirsty-christa-jaiprabhu123-318b4eef.koyeb.app
```

### **GET /api/reviews**
Extract reviews from a product page dynamically.

#### **URL**
```
https://thirsty-christa-jaiprabhu123-318b4eef.koyeb.app/api/reviews
```

#### **Query Parameters**
| Parameter | Type   | Description                            |
|-----------|--------|----------------------------------------|
| `url`     | string | The URL of the product page to scrape. |

#### **Example Request**
```bash
curl --location 'https://thirsty-christa-jaiprabhu123-318b4eef.koyeb.app/api/reviews?url=https%3A%2F%2Fbhumi.com.au%2Fproducts%2Fsateen-sheet-set-orion-blue'
```

#### **Example Response**
```json
{
    "reviews_count": 5,
    "reviews": [
        {
            "title": "Fantastic Sheets!",
            "body": "These are the softest sheets I have ever owned.",
            "rating": 5,
            "reviewer": "John Doe"
        },
        {
            "title": "Not worth the price",
            "body": "Expected better quality for the price.",
            "rating": 2,
            "reviewer": "Jane Smith"
        }
    ]
}
```

## Features
- Dynamically identifies CSS selectors for extracting reviews using **OpenAI**.
- Handles pagination to scrape all reviews on the product page.
- Cleans HTML content to focus on relevant data.
- Works seamlessly with modern e-commerce platforms like Shopify.

## How It Works
1. **Playwright** is used to load the product page and retrieve the complete HTML content, including dynamically loaded elements.
2. The HTML is cleaned and truncated to fit OpenAI token limits.
3. OpenAI is used to identify CSS selectors for:
   - Review titles
   - Review bodies
   - Ratings
   - Reviewer names
4. The API scrapes the reviews using the identified selectors.

## Installation

### Prerequisites
- Python 3.8 or higher
- Playwright dependencies installed (`playwright install-deps`)

### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install
   ```

4. Create a `.env` file and add your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. Run the application locally:
   ```bash
   python train.py
   ```

6. Access the API at `http://127.0.0.1:5000/api/reviews`.

## Deployment

### Procfile
Ensure your project includes a `Procfile` for deployment:
```plaintext
web: playwright install-deps && playwright install && gunicorn train:app --workers 4 --bind 0.0.0.0:$PORT
```

### Hosting on Koyeb
1. Push the project to GitHub.
2. Connect the GitHub repository to Koyeb.
3. Add the `OPENAI_API_KEY` environment variable in the Koyeb settings.
4. Deploy the project.

## Technologies Used
- **Flask**: Backend framework for creating the API.
- **Playwright**: Browser automation for scraping dynamic content.
- **OpenAI API**: Used for identifying dynamic CSS selectors.
- **Gunicorn**: WSGI server for production deployment.
- **Koyeb**: Cloud hosting platform for deployment.

## Troubleshooting

### Missing Dependencies
If the app fails with browser-related errors, ensure Playwright dependencies are installed:
```bash
playwright install-deps
```

### API Key Issues
- Ensure the OpenAI API key is correctly set in the `.env` file.
- Check the key's permissions and usage limits on the OpenAI dashboard.

### Logs
View deployment logs to debug errors:
```bash
koyeb logs -a <your-app-name>
```

## License
This project is licensed under the MIT License.



