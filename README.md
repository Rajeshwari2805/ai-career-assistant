# AI Career Assistant

A Python and Streamlit application that compares a resume with a job description, identifies matching and missing skills, calculates a keyword-based match score, and generates a personalized learning roadmap.

## Features
- Resume and job description input
- Required and preferred skill detection
- Resume skill matching
- Career match score
- Missing skill recommendations
- Personalized learning roadmap
- Optional local AI-based skill extraction using Ollama

## Technologies Used
- Python
- Streamlit
- Regular Expressions
- JSON
- Ollama

## Installation and Setup

1. Install Python.
2. Open the project folder in VS Code.
3. Install the dependencies:

   `pip install -r requirements.txt`

4. Run the application:

   `python -m streamlit run web_app.py`

5. Open the local URL displayed in the terminal.

## Optional Ollama Setup

Install Ollama and download the model:

`ollama pull llama3.2:3b`

The application can use keyword-based skill detection when the optional local AI functionality is unavailable.

## Limitations

The match score is based on detected keywords. It does not measure actual skill proficiency or predict hiring outcomes. Results depend on the wording of the resume and job description.

## Project Status

Core functionality implemented and manually tested with a sample resume and job description.