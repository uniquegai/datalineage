import streamlit as st
import requests
from groq import Groq
from config import groq_api_key
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os

GITHUB_API = "https://api.github.com"

def analyze_sql_script(sql_script):
    """
    Analyzes an SQL script and identifies source, temporary, destination tables and business logic using Groq API.
    """
    try:
        client = Groq(api_key=groq_api_key)

        prompts = {
            "source_tables": "List all source tables from which data is read in this SQL script.",
            "temporary_tables": "List any temporary or intermediate tables used during transformation. Prefix them as TEMP:<table_name>.",
            "destination_tables": "List the final destination tables where data is ultimately written.",
            "business_logic": "Explain the business logic applied during the transformation including filtering, joins, and aggregation."
        }

        results = {}

        for key, prompt in prompts.items():
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes SQL scripts."},
                    {"role": "user", "content": f"{prompt}\n\nSQL:\n{sql_script}"}
                ],
                max_tokens=400,
                temperature=0.3,
            )
            results[key] = response.choices[0].message.content.strip()

        return results["source_tables"], results["temporary_tables"], results["destination_tables"], results["business_logic"]

    except Exception as e:
        return "", "", "", f"Error analyzing script: {e}"


def draw_lineage_graph(source_str, temp_str, destination_str):
    net = Network(height='550px', width='100%', directed=True)
    net.barnes_hut()

    def parse_tables(table_str):
        return [t.strip() for t in table_str.split(",") if t.strip()]

    sources = parse_tables(source_str)
    temps = parse_tables(temp_str)
    destinations = parse_tables(destination_str)

    for table in sources:
        net.add_node(table, label=table, color="#FFFFFF", shape="ellipse")  # white: source

    for table in temps:
        label = table.replace("TEMP:", "")
        net.add_node(table, label=label, color="#FFD700", shape="box")  # yellow: temp

    for table in destinations:
        net.add_node(table, label=table, color="#4CAF50", shape="ellipse")  # green: final dest

    # Edge logic: source -> temp -> dest
    for src in sources:
        for temp in temps:
            net.add_edge(src, temp)
    for temp in temps:
        for dst in destinations:
            net.add_edge(temp, dst)
    if not temps:
        for src in sources:
            for dst in destinations:
                net.add_edge(src, dst)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)
        tmp_path = tmp_file.name

    with open(tmp_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    os.unlink(tmp_path)
    components.html(html_content, height=550, scrolling=True)


def list_sql_files(repo_owner, repo_name, access_token, path=""):
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
    st.title("🧠 SQL Data Lineage Analyzer with Groq & GitHub")

    sql_repo_url = st.text_input("🔗 GitHub Repository URL")
    access_token = st.text_input("🔐 GitHub Personal Access Token", type="password")

    if not sql_repo_url or not access_token:
        st.info("Please enter the GitHub repo and access token.")
        return

    try:
        parts = sql_repo_url.strip("/").split("/")
        repo_owner = parts[-2]
        repo_name = parts[-1].replace(".git", "")

        sql_files = list_sql_files(repo_owner, repo_name, access_token)
        if not sql_files:
            st.warning("No SQL files found.")
            return

        selected_file = st.selectbox("📄 Choose a SQL file", [f["name"] for f in sql_files])
        file_url = next(f["download_url"] for f in sql_files if f["name"] == selected_file)
        sql_script = get_sql_file_content(file_url, access_token)

        st.code(sql_script, language="sql")

        if st.button("🚀 Analyze"):
            source, temp, destination, logic = analyze_sql_script(sql_script)

            st.subheader("📊 Analysis Results")
            st.markdown(f"**Source Tables:** {source}")
            st.markdown(f"**Temporary Tables:** {temp}")
            st.markdown(f"**Destination Tables:** {destination}")
            st.markdown(f"**Business Logic:** {logic}")

            st.subheader("🧭 Lineage Diagram")
            draw_lineage_graph(source, temp, destination)

    except Exception as e:
        st.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
