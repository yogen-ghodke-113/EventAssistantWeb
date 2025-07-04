import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from rapidfuzz import process, fuzz
import os
from typing import List, Dict, Optional
import json
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from dotenv import load_dotenv
import logging
import time
# Removed voice input dependencies - keeping it text-only

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Page config for mobile responsiveness
st.set_page_config(
    page_title="Investor Event Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile responsiveness and styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .search-container {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .investor-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 4px solid #1f77b4;
    }
    
    .metric-box {
        background: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .ai-content {
        background: #e8f5e8;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #4caf50;
    }
    
    .news-item {
        background: #fff3e0;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #ff9800;
    }
    
    /* Enhanced mobile-first responsive design */
    @media screen and (max-width: 430px) {
        /* iPhone 15 Pro Max optimized styling */
        .main .block-container {
            padding: 1rem 0.5rem !important;
        }
        
        .stSelectbox > div > div {
            font-size: 16px !important;
        }
        
        .stMarkdown h1 {
            font-size: 1.5rem !important;
        }
        
        .stMarkdown h2 {
            font-size: 1.25rem !important;
        }
        
        .stMarkdown h3 {
            font-size: 1.1rem !important;
        }
        
        /* Better description text size on mobile */
        .stMarkdown div[style*="font-size: 16px"] {
            font-size: 18px !important;
            line-height: 1.6 !important;
        }
    }
    
    /* Fix dropdown scrolling on mobile */
    .stSelectbox [data-baseweb="popover"] {
        position: fixed !important;
        z-index: 9999 !important;
        max-height: 50vh !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
    }
    
    .stSelectbox [data-baseweb="popover"] > div {
        max-height: 50vh !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
    }
    
    .stSelectbox [data-baseweb="menu"] {
        max-height: 45vh !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
    }
    
    /* Prevent page scroll when dropdown is open on mobile */
    @media screen and (max-width: 768px) {
        .stSelectbox [data-baseweb="popover"] {
            position: fixed !important;
            left: 5% !important;
            right: 5% !important;
            max-width: 90vw !important;
            max-height: 60vh !important;
            overflow-y: auto !important;
            -webkit-overflow-scrolling: touch !important;
            touch-action: pan-y !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
            border-radius: 8px !important;
        }
    }
    
    /* Ensure dropdown appears correctly */
    .stSelectbox > div > div > div {
        flex-direction: column !important;
    }
    
    .stSelectbox [data-baseweb="popover"] > div {
        top: 100% !important;
        bottom: auto !important;
        transform: none !important;
    }
    
    .chat-input-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .user-message {
        background: #e3f2fd;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        border-left: 3px solid #2196f3;
    }
    
    .assistant-message {
        background: #f3e5f5;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        border-left: 3px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'investors_df' not in st.session_state:
    st.session_state.investors_df = None
if 'selected_investor' not in st.session_state:
    st.session_state.selected_investor = None
if 'ai_cache' not in st.session_state:
    st.session_state.ai_cache = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "search"
if 'citation_counter' not in st.session_state:
    st.session_state.citation_counter = 0
if 'citations_map' not in st.session_state:
    st.session_state.citations_map = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_company' not in st.session_state:
    st.session_state.current_company = None

@st.cache_data
def load_investor_data():
    """Load and cache investor data from CSV"""
    try:
        df = pd.read_csv('Yogen.csv')
        return df
    except FileNotFoundError:
        st.error("Yogen.csv file not found. Please make sure it's in the same directory as this app.")
        return None
    except Exception as e:
        st.error(f"Error loading CSV file: {str(e)}")
        return None

def setup_gemini_api():
    """Setup Gemini API with API key from environment variables"""
    # Try to get API key from environment variables first (.env file or system env)
    # Support both GEMINI_API_KEY (legacy) and GOOGLE_API_KEY (new SDK standard)
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    # Fallback to Streamlit secrets for cloud deployment
    if not api_key:
        try:
            api_key = st.secrets.get('GOOGLE_API_KEY') or st.secrets.get('GEMINI_API_KEY')
        except:
            api_key = None
    
    if not api_key:
        st.error("⚠️ Gemini API key not found!")
        st.info("**Setup Options:**")
        st.info("1. Create a `.env` file with: `GOOGLE_API_KEY=your_key_here` or `GEMINI_API_KEY=your_key_here`")
        st.info("2. Set environment variable: `export GOOGLE_API_KEY=your_key_here`")
        st.info("3. For Streamlit Cloud: Add to secrets as 'GOOGLE_API_KEY'")
        st.info("Get your API key at: https://makersuite.google.com/app/apikey")
        return False, None
    
    try:
        # Initialize client with new SDK structure
        client = genai.Client(api_key=api_key)
        return True, client
    except Exception as e:
        st.error(f"Error configuring Gemini API: {str(e)}")
        return False, None

def fuzzy_search_investors(query: str, df: pd.DataFrame, limit: int = 10) -> List[Dict]:
    """Perform fuzzy search on investor data"""
    if df is None or query.strip() == "":
        return []
    
    # Search in multiple fields
    search_fields = ['Investors', 'Name in PEI Event List', 'HQ Location', 'Primary Investor Type']
    all_matches = []
    
    for field in search_fields:
        if field in df.columns:
            # Get non-null values for the field
            field_values = df[field].dropna().astype(str).tolist()
            matches = process.extract(query, field_values, scorer=fuzz.partial_ratio, limit=limit)
            
            for match, score, idx in matches:
                if score > 60:  # Minimum score threshold
                    # Find the row with this value
                    matching_rows = df[df[field].astype(str) == match]
                    if not matching_rows.empty:
                        row = matching_rows.iloc[0]
                        all_matches.append({
                            'investor': row,
                            'score': score,
                            'matched_field': field,
                            'matched_value': match
                        })
    
    # Sort by score and remove duplicates
    seen_investors = set()
    unique_matches = []
    for match in sorted(all_matches, key=lambda x: x['score'], reverse=True):
        investor_name = match['investor']['Investors']
        if investor_name not in seen_investors:
            seen_investors.add(investor_name)
            unique_matches.append(match)
    
    return unique_matches[:limit]

def add_wikipedia_style_citations(response):
    """Add clean Wikipedia-style citations without affecting the main text"""
    if not response or not hasattr(response, 'text'):
        return ""
    
    text = response.text
    if not text:
        return ""
    
    # Check if response has grounding data
    try:
        if not hasattr(response, 'candidates') or not response.candidates:
            return text
        
        candidate = response.candidates[0]
        if not hasattr(candidate, 'grounding_metadata') or not candidate.grounding_metadata:
            return text
        
        grounding_metadata = candidate.grounding_metadata
        if not hasattr(grounding_metadata, 'grounding_supports') or not grounding_metadata.grounding_supports:
            return text
        
        supports = grounding_metadata.grounding_supports
        chunks = grounding_metadata.grounding_chunks if hasattr(grounding_metadata, 'grounding_chunks') else []
        
        if not supports or not chunks:
            return text
        
        # Clear previous citations for this response
        st.session_state.citation_counter = 0
        st.session_state.citations_map = {}
        
        # Process supports and collect unique URLs
        citation_urls = []
        for support in supports:
            if hasattr(support, 'grounding_chunk_indices') and support.grounding_chunk_indices:
                for chunk_idx in support.grounding_chunk_indices:
                    if chunk_idx < len(chunks) and hasattr(chunks[chunk_idx], 'web') and chunks[chunk_idx].web:
                        uri = chunks[chunk_idx].web.uri
                        # Filter out Google Vertex AI search URLs and get actual sources
                        if uri and 'vertexaisearch.cloud.google.com' not in uri and uri not in citation_urls:
                            citation_urls.append(uri)
        
        # Only add sources section at the end if we have real URLs
        if citation_urls:
            text += "\n\n## Sources\n"
            for i, uri in enumerate(citation_urls, 1):
                try:
                    domain = urlparse(uri).netloc.replace('www.', '') or uri
                    text += f"{i}. [{domain}]({uri})\n"
                except:
                    text += f"{i}. [Source]({uri})\n"
        
        return text
        
    except Exception as e:
        logger.error(f"Error processing citations: {str(e)}")
        return text

def get_gemini_response(prompt: str, cache_key: str = None) -> Optional[str]:
    """Get response from Gemini API with Google Search grounding and caching"""
    # Initialize processing_key early to avoid scoping issues
    processing_key = f"{cache_key}_processing" if cache_key else None
    
    logger.info(f"🔍 Starting API call for cache_key: {cache_key}")
    
    if cache_key and cache_key in st.session_state.ai_cache:
        logger.info(f"📋 Cache hit for key: {cache_key}")
        return st.session_state.ai_cache[cache_key]
    
    # Check if we're already processing this cache key to prevent duplicates
    if processing_key and processing_key in st.session_state:
        logger.info(f"⏳ Request already in progress for: {cache_key}")
        return "Loading..."
    
    if 'gemini_client' not in st.session_state:
        logger.error("❌ Gemini client not initialized")
        st.error("Gemini client not initialized")
        return None

    try:
        # Mark as processing to prevent duplicates
        if processing_key:
            st.session_state[processing_key] = True
            logger.info(f"🔒 Marked {processing_key} as processing")
        
        logger.info(f"🚀 Making Gemini API call with cache_key: {cache_key}")
        
        # Define the grounding tool
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Configure generation settings (use Flash for faster responses without thinking)
        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            response_modalities=["TEXT"],
            system_instruction="Provide direct, concise responses without internal reasoning steps."
        )

        # Make the request with 2.5 Flash (no thinking for speed)
        response = st.session_state.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )
        
        if response and response.text:
            result = response.text.strip()
            logger.info(f"✅ Raw response received, length: {len(result)} characters")
            
            # Fix monetary formatting issues by adding spaces around numbers and units
            # Handle specific patterns like "1-50million" -> "1-50 million"
            result = re.sub(r'(\d+)[-–](\d+)(million|billion|Million|Billion)', r'\1-\2 \3', result)
            # Handle standalone numbers with monetary units
            result = re.sub(r'(\d+)(million|billion|Million|Billion)', r'\1 \2', result)
            # Fix dollar amounts
            result = re.sub(r'(\$\d+)([a-zA-Z])', r'\1 \2', result)
            # Fix compound words like "andenterprise" -> "and enterprise"
            result = re.sub(r'(and)([A-Z][a-z])', r'\1 \2', result)
            result = re.sub(r'(to)([A-Z][a-z])', r'\1 \2', result)
            result = re.sub(r'(up)([A-Z][a-z])', r'\1 \2', result)
            result = re.sub(r'(values)([A-Z][a-z])', r'\1 \2', result)
            # General fix for number followed by capital letter
            result = re.sub(r'(\d)([A-Z][a-z])', r'\1 \2', result)
            
            # Add Wikipedia-style citations to the response
            text_with_citations = add_wikipedia_style_citations(response)
            
            if cache_key:
                st.session_state.ai_cache[cache_key] = text_with_citations
                logger.info(f"💾 Cached response for key: {cache_key}")
                # Clear processing flag
                if processing_key and processing_key in st.session_state:
                    del st.session_state[processing_key]
                    logger.info(f"🔓 Cleared processing flag for {processing_key}")
            return text_with_citations
        else:
            logger.warning("⚠️ Empty response from Gemini")
            # Clear processing flag
            if processing_key and processing_key in st.session_state:
                del st.session_state[processing_key]
                logger.info(f"🔓 Cleared processing flag after empty response")
            return "No response generated."
            
    except Exception as e:
        logger.error(f"❌ Error getting AI response: {str(e)}")
        logger.exception("Full traceback:")  # This will log the full stack trace
        # Clear processing flag on error
        if processing_key and processing_key in st.session_state:
            del st.session_state[processing_key]
            logger.info(f"🔓 Cleared processing flag after error")
        st.error(f"Error getting AI response: {str(e)}")
        return None

def generate_company_info(company_name: str) -> str:
    """Generate comprehensive AI content about the company with strict no-hallucination guidelines"""
    logger.info(f"🎯 Generating company info prompt for: {company_name}")
    
    prompt = f"""You are an AI research assistant providing factual, verifiable information about investment companies.

**CRITICAL REQUIREMENTS - NO HALLUCINATION ALLOWED:**

1. **VERIFICATION MANDATE**: Every single fact, figure, investment, or claim you make about "{company_name}" MUST be verifiable from real, current sources
2. **NO FABRICATION**: Do not invent portfolio companies, investment amounts, dates, or any other details
3. **SOURCE VERIFICATION**: If you cannot find verifiable information about something, explicitly state "Information not available" rather than guessing
4. **CURRENT DATA ONLY**: Use only recent, verifiable information - do not rely on potentially outdated training data
5. **CONSERVATIVE APPROACH**: When in doubt, provide less information rather than potentially incorrect information

**OBJECTIVE:**
Provide comprehensive, factual information about "{company_name}" in the following format:

## About the Company
[Provide a verifiable overview focusing on: founding year (if verifiable), headquarters location, key founders/leaders (if verifiable), and core mission. Only include information you can verify through current sources. 3-4 sentences maximum.]

## What They Do  
[Describe their verified investment focus, confirmed sectors of operation, and documented strategies. Only mention specific sectors, deal types, or strategies you can verify. 3-4 sentences maximum.]

## Major Investments
[List ONLY verified, documented portfolio companies or investments. Each entry must include:
- Company name (verified)
- Brief description of what the company does
- Investment type/date if verifiable
- Do NOT fabricate investment amounts or dates
- If fewer than 5 verified investments are found, list only what you can verify
- If no specific investments can be verified, state "Specific portfolio investments require verification"]

**FORMATTING REQUIREMENTS:**
- Use proper markdown formatting
- Be direct and factual
- Include disclaimer if information is limited
- Prioritize accuracy over completeness

**SOURCES PRIORITY ORDER:**
1. Official company website and press releases
2. SEC filings and regulatory documents  
3. Major financial news publications (Bloomberg, Reuters, WSJ)
4. Verified industry publications (Private Equity International, PE Hub)

Remember: It is better to provide limited verified information than extensive unverified claims."""
    
    cache_key = f"{company_name}_full_info"
    response = get_gemini_response(prompt, cache_key)
    return response or "Information not available."

def get_link_preview(url: str) -> Dict[str, str]:
    """Get basic link preview information with better error handling"""
    try:
        # Skip invalid URLs or Google vertex search URLs
        if not url or 'vertexaisearch.cloud.google.com' in url:
            return {
                'title': "Invalid link",
                'description': "Unable to preview this link",
                'domain': "unknown"
            }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.find('title')
        description = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        
        # Safe URL parsing
        try:
            domain = urlparse(url).netloc.replace('www.', '') if url else "unknown"
        except:
            domain = "unknown"
        
        return {
            'title': title.text.strip() if title else "No title available",
            'description': description.get('content', '').strip() if description else "No description available",
            'domain': domain
        }
    except Exception as e:
        try:
            domain = urlparse(url).netloc.replace('www.', '') if url else "unknown"
        except:
            domain = "unknown"
        return {
            'title': "Link preview unavailable",
            'description': f"Could not fetch preview: {str(e)[:50]}",
            'domain': domain
        }

def get_gemini_news_response(prompt: str, cache_key: str = None) -> Optional[str]:
    """Get response from Gemini 2.5 Pro with thinking enabled for news generation"""
    # Initialize processing_key early to avoid scoping issues
    processing_key = f"{cache_key}_processing" if cache_key else None
    
    logger.info(f"🔍 Starting news generation for cache_key: {cache_key}")
    
    if cache_key and cache_key in st.session_state.ai_cache:
        logger.info(f"📋 News cache hit for key: {cache_key}")
        return st.session_state.ai_cache[cache_key]
    
    # Check if we're already processing this cache key to prevent duplicates
    if processing_key and processing_key in st.session_state:
        logger.info(f"⏳ News request already in progress for: {cache_key}")
        return "Loading news..."
    
    # Simple rate limiting - don't allow more than 3 concurrent news requests
    active_news_requests = [k for k in st.session_state.keys() if k.endswith('_news_processing') or (k.endswith('_processing') and '_news_' in k)]
    if len(active_news_requests) >= 3:
        logger.info(f"🚦 Rate limit hit - {len(active_news_requests)} active news requests")
        return "Please wait, processing other news requests..."
    
    if 'gemini_client' not in st.session_state:
        logger.error("❌ Gemini client not initialized for news")
        st.error("Gemini client not initialized")
        return None
    
    try:
        # Mark as processing to prevent duplicates
        if processing_key:
            st.session_state[processing_key] = True
            logger.info(f"🔒 Marked {processing_key} as processing")
        
        logger.info(f"🚀 Making Gemini Pro API call for news with cache_key: {cache_key}")
        
        # Define the grounding tool
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Configure generation settings - USE PRO model with thinking enabled for better verification
        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            response_modalities=["TEXT"],
            # Enable thinking for better news verification (no system instruction to allow thinking)
        )

        # Make the request with 2.5 Pro model with thinking enabled for better news verification
        response = st.session_state.gemini_client.models.generate_content(
            model="gemini-2.5-pro",  # Use Pro model with thinking for news
            contents=prompt,
            config=config,
        )
        
        if response and response.text:
            logger.info(f"✅ News response received, length: {len(response.text)} characters")
            # Add clean citations without brackets in content
            text_with_citations = add_wikipedia_style_citations(response)
            if cache_key:
                st.session_state.ai_cache[cache_key] = text_with_citations
                logger.info(f"💾 Cached news response for key: {cache_key}")
            
            # Clear processing flag
            if processing_key and processing_key in st.session_state:
                del st.session_state[processing_key]
                logger.info(f"🔓 Cleared processing flag for {processing_key}")
            
            return text_with_citations
        else:
            logger.warning("⚠️ Empty news response from Gemini Pro")
            # Clear processing flag
            if processing_key and processing_key in st.session_state:
                del st.session_state[processing_key]
                logger.info(f"🔓 Cleared processing flag after empty response")
            return "No response generated."
            
    except Exception as e:
        logger.error(f"❌ Error getting news response: {str(e)}")
        logger.exception("Full traceback:")  # This will log the full stack trace
        # Clear processing flag on error
        if processing_key and processing_key in st.session_state:
            del st.session_state[processing_key]
            logger.info(f"🔓 Cleared processing flag after error")
        st.error(f"Error getting news response: {str(e)}")
        return None



def generate_news_articles(company_name: str) -> str:
    """Generate news articles using Gemini 2.5 Pro with thinking for verification"""
    logger.info(f"📰 Generating news prompt for: {company_name}")
    
    prompt = f"""Find REAL, VERIFIABLE news articles about "{company_name}" from the last 6 months.

**CRITICAL REQUIREMENT: NO HALLUCINATION**
- Every URL must be real and working
- Every headline must be from an actual article
- Every date must be accurate
- If you cannot find real articles, say "No verified news articles found"

**RESEARCH TASK:**
Find recent news articles about "{company_name}" (the investment firm/private equity company) from the last 6 months focusing on:
1. Major acquisitions or investments
2. Fund closings or capital raises
3. Strategic partnerships
4. Executive appointments or leadership changes
5. Portfolio company activities

**OUTPUT REQUIREMENTS:**
- Maximum 3 articles (for speed)
- Only include articles you can verify exist
- Use clean markdown formatting
- No bracketed numbers [1], [2], etc. in headlines or URLs
- Include working links only

**FORMAT:**

### [Actual Headline]
**Source:** [Real Publication Name]  
**Date:** [Actual Date]  
**Link:** [Working URL]  
**Summary:** [Brief factual summary]

**VERIFICATION STANDARD:**
Think through each article you want to include. Can you verify this is a real article from a real source? If not, don't include it. Better to find 2 real articles than 5 fake ones.

Please research and provide real news about {company_name}."""
    
    cache_key = f"{company_name}_news"
    response = get_gemini_news_response(prompt, cache_key)
    
    return response or "No recent verified news articles found."

def generate_chatbot_response(company_name: str, question: str, chat_history: List[Dict], company_metadata: Dict = None, company_insights: str = None, company_news: str = None) -> str:
    """Generate contextual chatbot response with sophisticated prompt engineering"""
    
    # Build company context from metadata and AI insights
    company_context = ""
    if company_metadata:
        company_context += "\n**COMPANY METADATA:**\n"
        company_context += f"Name: {company_metadata.get('Investors', 'N/A')}\n"
        company_context += f"Type: {company_metadata.get('Primary Investor Type', 'N/A')}\n"
        company_context += f"Location: {company_metadata.get('HQ Location', 'N/A')}, {company_metadata.get('HQ Country/Territory/Region', 'N/A')}\n"
        company_context += f"AUM: {company_metadata.get('AUM', 'N/A')}\n"
        company_context += f"PE Category: {company_metadata.get('PE Category', 'N/A')}\n"
        company_context += f"Total Investments: {company_metadata.get('Investments', 'N/A')}\n"
        company_context += f"Active Portfolio: {company_metadata.get('Active Portfolio', 'N/A')}\n"
        company_context += f"Exits: {company_metadata.get('Exits', 'N/A')}\n"
        company_context += f"Investments (Last 12 Months): {company_metadata.get('Investments in the last 12 months', 'N/A')}\n"
        company_context += f"Dry Powder: {company_metadata.get('Dry Powder', 'N/A')}\n"
        if company_metadata.get('Description'):
            company_context += f"Description: {company_metadata.get('Description')}\n"
    
    if company_insights:
        company_context += "\n**AI-GENERATED COMPANY INSIGHTS:**\n"
        company_context += company_insights + "\n"
    
    if company_news:
        company_context += "\n**RECENT NEWS & DEVELOPMENTS:**\n"
        company_context += company_news + "\n"
    
    # Build conversation context
    context = ""
    if chat_history:
        context = "\n**CONVERSATION HISTORY:**\n"
        for entry in chat_history[-6:]:  # Last 6 exchanges for context
            context += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n\n"
    
    # Build the conversation-aware prompt
    conversation_analysis = ""
    if chat_history:
        conversation_analysis = "**CONVERSATION ANALYSIS:**\n"
        conversation_analysis += f"We've had {len(chat_history)} exchanges about {company_name}. "
        
        # Analyze what has been discussed
        topics_discussed = []
        for exchange in chat_history:
            if "strategy" in exchange['user'].lower():
                topics_discussed.append("investment strategy")
            if "compare" in exchange['user'].lower() or "peer" in exchange['user'].lower():
                topics_discussed.append("competitive analysis")
            if "performance" in exchange['user'].lower():
                topics_discussed.append("performance metrics")
            if "portfolio" in exchange['user'].lower():
                topics_discussed.append("portfolio analysis")
        
        if topics_discussed:
            conversation_analysis += f"Previous topics covered: {', '.join(set(topics_discussed))}. "
        
        # Check if this is a follow-up question
        follow_up_indicators = ["what", "how", "why", "tell me more", "explain", "elaborate", "details"]
        if any(indicator in question.lower() for indicator in follow_up_indicators) and len(question.split()) < 5:
            conversation_analysis += "This appears to be a follow-up question requiring context from our previous discussion. "

    prompt = f"""You are ARIA, an expert investment analyst having a dynamic conversation about {company_name}. Be conversational, specific, and NEVER repeat the same information.

{company_context}

{conversation_analysis}

**CONVERSATION HISTORY:**
{context}

**CURRENT QUESTION:** "{question}"

**CRITICAL INSTRUCTIONS:**
1. **NO REPETITION**: If you've already discussed something, don't repeat it. Build on it or explore new angles.
2. **BE CONVERSATIONAL**: This is a dialogue, not a report. Respond naturally to follow-up questions.
3. **USE SPECIFIC DATA**: Reference the actual numbers from the company metadata (AUM: {company_metadata.get('AUM', 'N/A') if company_metadata else 'N/A'}, Investments: {company_metadata.get('Investments', 'N/A') if company_metadata else 'N/A'}, etc.)
4. **CONTEXT AWARENESS**: If the user asks "What" or "How" or similar short questions, they're asking about the previous topic.
5. **VARY YOUR RESPONSES**: Each answer should feel fresh and explore different aspects.

**RESPONSE STYLE:**
- Keep it to 2-3 sentences maximum
- Be specific and data-driven using the provided metrics
- If it's a follow-up, directly reference what we discussed before
- Offer new insights or angles on the topic
- Be conversational, not robotic

**FOR FOLLOW-UP QUESTIONS:**
- If user asks "What?" after discussing strategy, explain specifics about their strategy
- If user asks "How?" after mentioning performance, explain their approach
- If user asks "Why?" after any statement, provide reasoning or context
- Always connect back to the specific data about this company

Answer the question naturally, as if you're an expert who has been studying this company and can provide specific insights based on their actual metrics and data:"""
    
    # Create more unique cache key to prevent conflicts
    import hashlib
    import time
    unique_str = f"{company_name}_{question}_{len(chat_history)}_{str(time.time())[:10]}"
    cache_key = f"chat_{hashlib.md5(unique_str.encode()).hexdigest()[:8]}"
    response = get_gemini_response(prompt, cache_key)
    
    return response or "I apologize, but I'm unable to provide a response at the moment. Please try rephrasing your question."

def format_value(value, default="N/A"):
    """Format a value, replacing NaN/empty values with N/A"""
    if value is None or pd.isna(value) or str(value).lower() in ['nan', '', '#n/a']:
        return default
    return str(value)

def get_all_company_names(df: pd.DataFrame) -> List[str]:
    """Get all unique company names from the CSV"""
    if df is None:
        return []
    
    names = []
    if 'Investors' in df.columns:
        names.extend(df['Investors'].dropna().astype(str).unique().tolist())
    if 'Name in PEI Event List' in df.columns:
        alt_names = df['Name in PEI Event List'].dropna().astype(str).unique().tolist()
        for name in alt_names:
            if name not in names and name != '#N/A':
                names.append(name)
    
    return sorted([name for name in names if name and name.strip()])

def get_search_suggestions(query: str, company_names: List[str]) -> List[str]:
    """Get search suggestions based on fuzzy matching"""
    if not query or len(query) < 1:
        return []
    
    query = query.lower()
    suggestions = []
    
    # First, add exact matches and starts-with matches
    for name in company_names:
        if query in name.lower():
            suggestions.append(name)
    
    # Then add fuzzy matches if we don't have enough
    if len(suggestions) < 10:
        fuzzy_matches = process.extract(query, company_names, scorer=fuzz.partial_ratio, limit=10)
        for match, score, _ in fuzzy_matches:
            if score > 60 and match not in suggestions:
                suggestions.append(match)
    
    return suggestions[:10]

def search_page():
    """Display the search page with proper dropdown search"""
    st.title("💼 Investor Event Assistant")
    st.markdown("*Find and learn about investment companies with AI-powered insights*")
    
    # Load data
    df = st.session_state.investors_df
    if df is None:
        st.error("Data not loaded. Please refresh the page.")
        return
    
    # Get all company names for dropdown
    if 'all_company_names' not in st.session_state:
        st.session_state.all_company_names = get_all_company_names(df)
    
    company_names = st.session_state.all_company_names
    
    # Search interface with clean styling
    st.markdown("## 🔍 Search Investors")
    st.markdown("*Find investment companies using the search box below*")
    
    # Dropdown search with all company names
    selected_company = st.selectbox(
        "Select or search for a company:",
        options=[""] + company_names,
        index=0,
        format_func=lambda x: "Type to search..." if x == "" else x,
        help="Start typing to filter companies",
        key="company_selectbox"
    )
    
    # If a company is selected, find and display it
    if selected_company:
        # Find the investor data for the selected company
        investor_row = None
        
        # Search in both Investors and Name in PEI Event List columns
        matches = df[df['Investors'] == selected_company]
        if matches.empty:
            matches = df[df['Name in PEI Event List'] == selected_company]
        
        if not matches.empty:
            investor_row = matches.iloc[0]
            
            # Display the selected investor
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{investor_row['Investors']}**")
                st.markdown(f"*{format_value(investor_row.get('Primary Investor Type'))} | {format_value(investor_row.get('HQ Location'))}*")
                
                # Convert AUM from millions to billions for consistency
                aum_raw = investor_row.get('AUM', '')
                if aum_raw and pd.notna(aum_raw) and str(aum_raw).replace('.', '').replace('-', '').isdigit():
                    try:
                        aum_billions = float(aum_raw) / 1000
                        aum_display = f"${aum_billions:.1f}B"
                    except (ValueError, TypeError):
                        aum_display = format_value(aum_raw)
                else:
                    aum_display = format_value(aum_raw)
                
                st.markdown(f"AUM: {aum_display}")
            
            with col2:
                if st.button("View Details", key=f"btn_{investor_row['Investors']}", type="primary"):
                    st.session_state.selected_investor = investor_row
                    st.session_state.current_page = "details"
                    st.rerun()
        else:
            st.error("Company not found in database.")

def details_page():
    """Display the details page with auto-loading insights"""
    investor_row = st.session_state.selected_investor
    
    if investor_row is None:
        st.error("No investor selected")
        return
    
    # Back button
    if st.button("← Back to Search", key="back_button"):
        st.session_state.current_page = "search"
        st.session_state.selected_investor = None
        st.rerun()
    
    st.markdown(f"# {investor_row['Investors']}")
    
    # Header information with clean, distinct styling
    location = format_value(investor_row.get("HQ Location"))
    country = format_value(investor_row.get("HQ Country/Territory/Region"))
    location_display = f"{location}, {country}" if location != "N/A" and country != "N/A" else (location if location != "N/A" else country)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 15px 0; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div style="color: white; margin: 5px 0;">
                <span style="font-size: 14px; opacity: 0.9;">TYPE</span><br>
                <span style="font-size: 18px; font-weight: bold;">{format_value(investor_row.get("Primary Investor Type"))}</span>
            </div>
            <div style="color: white; margin: 5px 0; text-align: right;">
                <span style="font-size: 14px; opacity: 0.9;">LOCATION</span><br>
                <span style="font-size: 18px; font-weight: bold;">{location_display}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics Section with better formatting
    st.markdown("## 📊 Key Metrics")
    
    # Create a 3-column layout for better visual balance
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Convert AUM from millions to billions
        aum_raw = investor_row.get('AUM', '')
        if aum_raw and pd.notna(aum_raw) and str(aum_raw).replace('.', '').replace('-', '').isdigit():
            try:
                aum_billions = float(aum_raw) / 1000
                aum_display = f"${aum_billions:.1f}B"
            except (ValueError, TypeError):
                aum_display = format_value(aum_raw)
        else:
            aum_display = format_value(aum_raw)
        
        st.markdown(f'<div style="background: #e8f5e8; padding: 16px; border-radius: 8px; text-align: center; margin: 5px 0;"><h4 style="margin: 0; color: #2e7d32;">AUM (Billions)</h4><h3 style="margin: 0; color: #1b5e20;">{aum_display}</h3></div>', unsafe_allow_html=True)
        
        pe_category = format_value(investor_row.get('PE Category'))
        st.markdown(f'<div style="background: #fff3e0; padding: 16px; border-radius: 8px; text-align: center; margin: 5px 0;"><h4 style="margin: 0; color: #ef6c00;">PE Category</h4><h3 style="margin: 0; color: #bf360c;">{pe_category}</h3></div>', unsafe_allow_html=True)
    
    with col2:
        active_portfolio = format_value(investor_row.get('Active Portfolio'))
        st.markdown(f'<div style="background: #f3e5f5; padding: 16px; border-radius: 8px; text-align: center; margin: 5px 0;"><h4 style="margin: 0; color: #7b1fa2;">Active Portfolio</h4><h3 style="margin: 0; color: #4a148c;">{active_portfolio}</h3></div>', unsafe_allow_html=True)
        
        exits = format_value(investor_row.get('Exits'))
        st.markdown(f'<div style="background: #fce4ec; padding: 16px; border-radius: 8px; text-align: center; margin: 5px 0;"><h4 style="margin: 0; color: #c2185b;">Exits</h4><h3 style="margin: 0; color: #880e4f;">{exits}</h3></div>', unsafe_allow_html=True)
    
    with col3:
        last_12_months = format_value(investor_row.get('Investments in the last 12 months'))
        st.markdown(f'<div style="background: #e0f2f1; padding: 16px; border-radius: 8px; text-align: center; margin: 5px 0;"><h4 style="margin: 0; color: #00695c;">Last 12 Months</h4><h3 style="margin: 0; color: #004d40;">{last_12_months}</h3></div>', unsafe_allow_html=True)
    

    
    # Description from CSV with improved mobile formatting
    if pd.notna(investor_row.get('Description', '')):
        st.markdown("## 📋 Description")
        description_text = investor_row["Description"]
        st.markdown(f'<div style="background: #e8f5e8; padding: 16px; border-radius: 8px; border-left: 4px solid #4caf50; font-size: 16px; line-height: 1.5;">{description_text}</div>', unsafe_allow_html=True)
    
    # Progressive AI Content Loading
    st.markdown("---")
    company_cache_key = f"{investor_row['Investors']}_full_info"
    news_cache_key = f"{investor_row['Investors']}_news"
    
    # Load and display AI company insights immediately
    company_name = investor_row['Investors']
    logger.info(f"🏢 Starting company info load for: {company_name}")
    
    company_info = st.session_state.ai_cache.get(company_cache_key)
    if not company_info:
        # Show loading message for company info
        company_loading = st.empty()
        company_loading.info("🚀 Loading AI insights...")
        logger.info(f"💭 Company info not cached, generating for: {company_name}")
        
        try:
            company_info = generate_company_info(company_name)
            if company_info:
                st.session_state.ai_cache[company_cache_key] = company_info
                company_loading.empty()
                logger.info(f"✅ Company info loaded and cached for: {company_name}")
        except Exception as e:
            logger.error(f"❌ Error loading company info for {company_name}: {str(e)}")
            logger.exception("Company info loading error traceback:")
            company_loading.error(f"❌ Error loading AI insights: {str(e)}")
            company_info = "Error loading company information."
    else:
        logger.info(f"📋 Company info cache hit for: {company_name}")
    
    # Display company information immediately when available
    if company_info:
        st.markdown(company_info)
    
    # Recent News Section - Load separately
    st.markdown("---")
    st.markdown("## 📰 Recent News")
    
    # Load news separately (doesn't block company info display)
    logger.info(f"📰 Starting news load for: {company_name}")
    
    news_content = st.session_state.ai_cache.get(news_cache_key)
    if not news_content:
        # Show loading message for news
        news_loading = st.empty()
        news_loading.info("🚀 Loading recent news...")
        logger.info(f"📡 News not cached, generating for: {company_name}")
        
        try:
            news_content = generate_news_articles(company_name)
            if news_content:
                st.session_state.ai_cache[news_cache_key] = news_content
                news_loading.empty()
                logger.info(f"✅ News loaded and cached for: {company_name}")
        except Exception as e:
            logger.error(f"❌ Error loading news for {company_name}: {str(e)}")
            logger.exception("News loading error traceback:")
            news_loading.error(f"❌ Error loading news: {str(e)}")
            news_content = "Error loading news articles."
    else:
        logger.info(f"📋 News cache hit for: {company_name}")
    
    # Display news content
    if news_content and news_content != "No recent verified news articles found.":
        st.markdown(news_content)
    else:
        st.info("No recent verified news articles found for this company.")
        
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh All Content", key="refresh_all", use_container_width=True):
            # Clear cache and reload
            if company_cache_key in st.session_state.ai_cache:
                del st.session_state.ai_cache[company_cache_key]
            if news_cache_key in st.session_state.ai_cache:
                del st.session_state.ai_cache[news_cache_key]
            st.rerun()
    
    # AI Research Assistant Chatbot Section
    st.markdown("---")
    st.markdown("## 🤖 ARIA - Advanced Research Assistant")
    st.markdown("*Ask detailed questions about this company - powered by sophisticated AI analysis*")
    
    # Set current company for chat context
    if st.session_state.current_company != investor_row['Investors']:
        st.session_state.current_company = investor_row['Investors']
        st.session_state.chat_history = []  # Reset chat history for new company
    
    # Chat input section with form for Enter-to-send
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            chat_question = st.text_input(
                "Ask anything about this company:",
                placeholder="e.g., What is their investment strategy? How do they compare to peers?",
                key="chat_input",
                label_visibility="collapsed"
            )
        with col2:
            submit_button = st.form_submit_button("🚀 Ask", type="primary", use_container_width=True)
    
    # Process chat when form is submitted
    if submit_button and chat_question:
        with st.spinner("ARIA is analyzing your question..."):
            logger.info(f"Processing chat question: {chat_question[:50]}...")
            
            # Get company insights and news for context
            company_insights = st.session_state.ai_cache.get(company_cache_key, "")
            news_content = st.session_state.ai_cache.get(news_cache_key, "")
            
            # Convert investor_row to dict for metadata
            company_metadata = investor_row.to_dict() if hasattr(investor_row, 'to_dict') else dict(investor_row)
            
            response = generate_chatbot_response(
                investor_row['Investors'], 
                chat_question, 
                st.session_state.chat_history,
                company_metadata=company_metadata,
                company_insights=company_insights,
                company_news=news_content
            )
            
            # Add to chat history
            st.session_state.chat_history.append({
                'user': chat_question,
                'assistant': response
            })
            
            logger.info(f"Added chat exchange to history. Total exchanges: {len(st.session_state.chat_history)}")
            st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        
        for i, exchange in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 exchanges
            # User message with custom styling
            st.markdown(f'<div class="user-message"><strong>💭 You:</strong> {exchange["user"]}</div>', unsafe_allow_html=True)
            
            # Assistant response with custom styling
            st.markdown(f'<div class="assistant-message"><strong>🤖 ARIA:</strong> {exchange["assistant"]}</div>', unsafe_allow_html=True)
            
            if i < len(st.session_state.chat_history[-5:]) - 1:
                st.markdown("---")
        
        # Clear chat history button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear Chat History", key="clear_chat", use_container_width=True):
                st.session_state.chat_history = []
                logger.info("Chat history cleared")
                st.rerun()

def main():
    """Main application function with two-page structure"""
    # Setup
    api_success, client = setup_gemini_api()
    if not api_success:
        st.stop()
    
    # Store client in session state
    st.session_state.gemini_client = client
    
    # Load data
    if st.session_state.investors_df is None:
        with st.spinner("Loading investor data..."):
            st.session_state.investors_df = load_investor_data()
    
    df = st.session_state.investors_df
    if df is None:
        st.stop()
    
    # Page routing
    if st.session_state.current_page == "search":
        search_page()
    elif st.session_state.current_page == "details":
        details_page()

if __name__ == "__main__":
    main() 