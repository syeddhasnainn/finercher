# Earnings Report Analyzer

This project is a Python-based tool that analyzes earnings reports for selected companies using AI-powered sentiment analysis.

## Features

- Fetches latest earnings reports from multiple sources
- Performs sentiment analysis on the reports using OpenAI's GPT model
- Displays results in a rich, color-coded table
- Allows users to select a company from the latest earnings releases

## Prerequisites

- Python 3.7+
- OpenAI API key
- Tavily API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/earnings-report-analyzer.git
   cd earnings-report-analyzer
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```
