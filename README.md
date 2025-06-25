# 💼 Investor Event Assistant

A simple, mobile-responsive web app built with Streamlit to help during investor events by providing comprehensive information about investment companies through fuzzy search and AI-powered insights.

## Features

- 🔍 **Fuzzy Search**: Find investment companies with partial matching across names, locations, and types
- 📊 **Detailed Profiles**: View comprehensive company information including AUM, investments, and key metrics
- 🤖 **AI Insights**: Get AI-generated insights about companies using Google Gemini
- 📰 **News Integration**: Fetch recent news articles about investment companies
- 📱 **Mobile Responsive**: Optimized for both desktop and mobile devices
- ⚡ **Fast Deployment**: Deploy easily on Streamlit Cloud

## Quick Start

### Local Development

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd EventAssistantWeb
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key**

   Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

   **Option A: .env file (Recommended for local development)**

   ```bash
   # Create a .env file in the root directory
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

   **Option B: Environment Variable**

   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

   **Option C: Streamlit Secrets (for deployment)**

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit secrets.toml and add your API key
   ```

4. **Make sure your CSV file is in place**

   Ensure `Yogen.csv` is in the root directory

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

### Deploy to Streamlit Cloud

1. **Push your code to GitHub**

2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**

3. **Deploy your app**:

   - Connect your GitHub repository
   - Select the `app.py` file
   - Add your `GEMINI_API_KEY` in the secrets section

4. **Your app will be live at**: `https://your-app-name.streamlit.app`

## Project Structure

```
EventAssistantWeb/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── Yogen.csv                      # Investor data
├── README.md                      # This file
└── .streamlit/
    ├── config.toml                # Streamlit configuration
    └── secrets.toml.example       # Template for API keys
```

## Usage

1. **Search**: Enter a company name, location, or type in the search box
2. **Browse Results**: View fuzzy-matched results with match scores
3. **View Details**: Click "View Details" to see comprehensive company information
4. **AI Insights**: Generate AI-powered insights about the company
5. **Recent News**: Get recent news articles about the company

## Tech Stack

- **Frontend & Backend**: Streamlit (Python)
- **Data Processing**: Pandas
- **Search**: RapidFuzz (fuzzy string matching)
- **AI**: Google Generative AI (Gemini)
- **Deployment**: Streamlit Cloud

## Mobile Responsiveness

The app is designed to work seamlessly on:

- 📱 Mobile phones
- 📟 Tablets
- 💻 Desktop computers

Custom CSS ensures optimal viewing experience across all devices.

## Environment Variables

| Variable         | Description                | Required |
| ---------------- | -------------------------- | -------- |
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes      |

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational and demo purposes.
