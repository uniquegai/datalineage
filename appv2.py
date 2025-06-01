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

    # Set the app repository URL
    app_repo_url = "https://github.com/uniquegai/dlineage"

    # Get SQL scripts repository URL and personal access token from the user
    sql_repo_url = st.text_input("SQL Scripts Repository URL")
    access_token = st.text_input("Personal Access Token", type="password")

    if not sql_repo_url or not access_token:
        st.warning("Please provide the SQL Scripts Repository URL and personal access token.")
        return

    # Clone the SQL scripts repository
    try:
        sql_repo_name = sql_repo_url.split("/")[-1].replace(".git", "")
        sql_clone_path = os.path.join(".", sql_repo_name)
        
        # Construct the clone URL with the access token
        clone_url = sql_repo_url.replace("https://", f"https://{access_token}:x-oauth-basic@")
        
        clone_command = f"git clone {clone_url} {sql_clone_path}"
        subprocess.run(clone_command, shell=True, check=True)
        
    except Exception as e:
        st.error(f"Error cloning SQL scripts repository: {e}")
        return

    # Get list of SQL files from the cloned repository
    sql_files = [f for f in os.listdir(sql_clone_path) if f.endswith(".sql")]

    if not sql_files:
        st.warning("No SQL files found in the SQL scripts repository.")
        return

    # Select SQL file to analyze
    selected_sql_file = st.selectbox("Select SQL file", sql_files)

    # Read SQL script from the selected file
    sql_script_path = os.path.join(sql_clone_path, selected_sql_file)
    with open(sql_script_path, "r") as f:
        sql_script = f.read()

    # Analyze SQL script
    source_tables, destination_tables, business_logic = analyze_sql_script(sql_script)

    # Display analysis results
    st.subheader("Analysis Results")
    st.write(f"**Source Tables:** {source_tables}")
    st.write(f"**Destination Tables:** {destination_tables}")
    st.write(f"**Business Logic:** {business_logic}")

if __name__ == "__main__":
    main()
