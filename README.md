```md
# NewsSentimentVoice

**NewsSentimentVoice** is a web-based application that extracts news articles from multiple sources, performs sentiment analysis, and generates a comparative sentiment report. The report is then translated to Hindi and converted into a TTS (text-to-speech) audio file. The application also sorts articles by their relevance to a provided company name using fuzzy matching.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [API and Frontend](#api-and-frontend)
- [Deployment](#deployment)
- [License](#license)
- [Contact](#contact)

## Overview

In today's fast-paced digital world, staying updated with news is essential. **NewsSentimentVoice** automates the process of fetching and analyzing news articles, providing:
- A detailed sentiment analysis (Positive, Negative, or Neutral)
- A comparative sentiment report with overall statistics
- A Hindi audio summary generated from the report
- Sorted articles based on their relevance to a searched company name using fuzzy matching

## Features

- **Dynamic News Extraction:**  
  Scrapes news articles from various sources with robust error handling and retries.
- **Sentiment Analysis:**  
  Utilizes NLTK's VADER to analyze article summaries and classify sentiment.
- **Fuzzy Relevance Sorting:**  
  Uses RapidFuzz to rank articles based on how relevant they are to the provided company name.
- **Comparative Analysis:**  
  Generates a summary report displaying total articles and sentiment distribution.
- **Text-to-Speech (TTS):**  
  Translates the report to Hindi and creates an audio file using gTTS.
- **Interactive Gradio Interface:**  
  A user-friendly interface that lets users input a company name and view results interactively.

## Technologies Used

- **Backend & Web Scraping:** Python, BeautifulSoup, Requests
- **NLP & Sentiment Analysis:** NLTK (VADER)
- **Text-to-Speech:** gTTS, Deep-Translator
- **Fuzzy Matching:** RapidFuzz
- **User Interface:** Gradio
- **Deployment:** Hugging Face Spaces (or local deployment)

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git

### Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/NewsSentimentVoice.git
   cd NewsSentimentVoice


2. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK Data:**
   The application will automatically download necessary NLTK data (like `vader_lexicon`) on first run.

## Usage

### Running the Application Locally

To run the Gradio-based application locally, execute:
```bash
python frontend.py
```
This will launch the application and provide a local URL to access it.

### How to Use

- **Input:**  
  Enter the company name (e.g., "Tesla") in the provided textbox.
- **Output:**  
  - A comparative sentiment report will be displayed.
  - A sentiment distribution summary is provided.
  - Detailed article information, sorted by relevance, is shown.
  - A Hindi TTS audio file is generated and can be played within the interface.

## API and Frontend

- **Backend Processing:**  
  Core functionality is implemented in `utils.py`, which handles scraping, sentiment analysis, fuzzy matching, and TTS generation.
- **User Interface:**  
  The Gradio interface (`frontend.py`) gathers user input and displays results interactively.

## Deployment

This project can be deployed on Hugging Face Spaces:

1. **Create a New Space:**  
   Log in to [Hugging Face Spaces](https://huggingface.co/spaces) and create a new Space using the Gradio template.
2. **Push Your Code:**  
   Connect your repository or push your files (including `frontend.py` and `requirements.txt`) to the Space.
3. **Automatic Deployment:**  
   The environment will be built based on `requirements.txt` and your app will be accessible via the provided Space URL.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact:
- **P.V. Tharun Raj**
- Email: [tharuunnnn.gmail.com](mailto:tharuunnnn.gmail.com)
- LinkedIn: [Tharunn Raj](https://www.linkedin.com/in/tharunnraj/)
```

