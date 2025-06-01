import streamlit as st
import requests
from groq import Groq
from config import groq_api_key

GITHUB_API = "https://api.github.com"

def analyze_sql_script(sql_script):
    """
    Analyzes an SQL script and identifies source tables, destination tables, and business logic using Groq API.
    """
    try:
        client = Groq(api_key=groq_api_key)

        prompts = {
            "source_tables": "Provide the source tables:",
            "destination_tables": "Provide the destination tables:",
            "business_logic": "Provide the business logic:"
        }

        results = {}

        for key, prompt in prompts.items():
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes SQL scripts."},
                    {"role": "user", "content": f"Analyze the following SQL script and identify source tables, destination tables, and business logic. {prompt}\n\n{sql_script}"}
                ],
                max_tokens=300,
                temperature=0.3,
            )
            results[key] = response.choices[0].message.content.strip()

        return results["source_tables"], results["destination_tables"], results["business_logic"]
    except Exception as e:
        return "", "", f"Error analyzing script: {e}"


def list_sql_files(repo_owner, repo_name, access_token, path=""):
    """Lists .sql files in a GitHub repo using GitHub API"""
    url = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.text}")
    files = response.json()
    return [f for f in files if f["name"].endswith(".sql") and f["type"] == "file"]


def get_sql_file_content(file_url, access_token):
    headers = {"Authorization": f"token {access_token}"}
    response = requests.get(file_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error reading file: {response.text}")
    return response.text


def main():
    st.title("🔍 Data Lineage Analyzer")

    sql_repo_url = st.text_input("🔗 GitHub Repository URL (e.g., https://github.com/user/repo)")
    access_token = st.text_input("🔐 GitHub Personal Access Token", type="password")

    if not sql_repo_url or not access_token:
        st.warning("Please enter the repository URL and access token.")
        return

    try:
        path_parts = sql_repo_url.strip("/").split("/")
        repo_owner = path_parts[-2]
        repo_name = path_parts[-1].replace(".git", "")

        sql_files = list_sql_files(repo_owner, repo_name, access_token)

        if not sql_files:
            st.warning("No .sql files found in the repo.")
            return

        selected_file = st.selectbox("📄 Select a SQL file", [f["name"] for f in sql_files])
        file_url = next(f["download_url"] for f in sql_files if f["name"] == selected_file)
        sql_script = get_sql_file_content(file_url, access_token)

        st.code(sql_script, language="sql")

        if st.button("🚀 Analyze SQL"):
            source, destination, logic = analyze_sql_script(sql_script)

            st.subheader("📊 Analysis Results")
            st.markdown(f"**Source Tables:** {source}")
            st.markdown(f"**Destination Tables:** {destination}")
            st.markdown(f"**Business Logic:** {logic}")

    except Exception as e:
        st.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
