import streamlit as st
import os
import subprocess
from groq import Groq
from config import groq_api_key

def analyze_sql_script(sql_script):
    """
    Analyzes an SQL script and identifies source tables, destination tables, and business logic using Groq API.
    """
    try:
        client = Groq(api_key=groq_api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes SQL scripts."},
                {"role": "user", "content": f"Analyze the following SQL script and identify source tables, destination tables, and business logic. Provide the source tables:\n\n{sql_script}"}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        source_tables = response.choices[0].message.content.strip()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes SQL scripts."},
                {"role": "user", "content": f"Analyze the following SQL script and identify source tables, destination tables, and business logic. Provide the destination tables:\n\n{sql_script}"}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        destination_tables = response.choices[0].message.content.strip()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes SQL scripts."},
                {"role": "user", "content": f"Analyze the following SQL script and identify source tables, destination tables, and business logic. Provide the business logic:\n\n{sql_script}"}
            ],
            max_tokens=250,
            n=1,
            stop=None,
            temperature=0.7,
        )
        business_logic = response.choices[0].message.content.strip()

        return source_tables, destination_tables, business_logic
    except Exception as e:
        return "", "", f"Error analyzing script: {e}"


def main():
    st.title("Data Lineage Analyser")

    # Get GitHub repository URL and personal access token from the user
    repo_url = st.text_input("GitHub Repository URL")
    access_token = st.text_input("Personal Access Token", type="password")

    if not repo_url or not access_token:
        st.warning("Please provide the GitHub repository URL and personal access token.")
        return

    # Clone the repository
    try:
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        clone_path = os.path.join(".", repo_name)
        
        # Construct the clone URL with the access token
        clone_url = repo_url.replace("https://", f"https://{access_token}@")
        
        clone_command = f"git clone {clone_url} {clone_path}"
        subprocess.run(clone_command, shell=True, check=True)
        os.chdir(clone_path)
    except Exception as e:
        st.error(f"Error cloning repository: {e}")
        return

    # Get list of SQL files from the cloned repository
    sql_files = [f for f in os.listdir(".") if f.endswith(".sql")]

    if not sql_files:
        st.warning("No SQL files found in the repository.")
        return

    # Select SQL file to analyze
    selected_sql_file = st.selectbox("Select SQL file", sql_files)

    # Read SQL script from the selected file
    with open(selected_sql_file, "r") as f:
        sql_script = f.read()

    # Analyze SQL script
    source_tables, destination_tables, business_logic = analyze_sql_script(sql_script)

    # Display analysis results
    st.subheader("Analysis Results")
    st.write(f"**Source Tables:** {source_tables}")
    st.write(f"**Destination Tables:** {destination_tables}")
    st.write(f"**Business Logic:** {business_logic}")

if __name__ == "__main__":
    # Change current directory to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
