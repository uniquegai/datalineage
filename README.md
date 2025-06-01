# Data Lineage Analyser (appv2.py)

This Streamlit app analyzes SQL scripts from a GitHub repository and identifies source tables, destination tables, and business logic using the Groq API.

## Prerequisites

*   Python 3.7 or higher
*   Streamlit
*   Groq Python library

## Setup

1.  Create a virtual environment:

    ```bash
    python -m venv venv
    ```
2.  Activate the virtual environment:

    ```bash
    venv\\Scripts\\activate
    ```
3.  Install the required libraries:

    ```bash
    pip install streamlit groq
    ```

## Usage

1.  Run the Streamlit app:

    ```bash
    streamlit run appv2.py
    ```
2.  Enter the GitHub repository URL and your personal access token in the Streamlit app.
3.  Select an SQL file from the repository to analyze.
4.  The app will display the analysis results from the Groq API.

## Configuration

The Groq API key is stored in the `config.py` file. You can update the API key in this file:

```python
groq_api_key = "YOUR_GROQ_API_KEY"
```

## Notes

*   The data lineage visualization feature has been removed due to environment issues.
*   You need to have a valid Groq API key to use this app.
