import streamlit as st
import arxiv
import requests
import PyPDF2
import tiktoken
import os
import openai
import pandas as pd
from io import BytesIO
# import threading

openai.api_key = os.getenv("OPENAI_API_KEY")

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(text))

def sanitize_filename(filename):
    invalid_chars = set(r'\/:*?"<>|')
    return "_".join("".join(c for c in filename if c not in invalid_chars).split())

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_article_pdf(url):
    response = requests.get(url)
    pdf = PyPDF2.PdfReader(BytesIO(response.content))
    return ''.join(page.extract_text() for page in pdf.pages)

def sanitize_article_text(text):
    return text.split("REFERENCES", 1)[0]

def save_article(save_path, text):
    with open(save_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(text)

def summarize_article(text):
    text = text[:count_tokens(text) if count_tokens(text) <= 15000 else 15000]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        stream=True,
        max_tokens=800,
        messages=[
            {"role": "system",
             "content": "You are a high-level AI assistant capable of comprehending and summarizing complex scientific content. Your task is to digest this scientific paper and present the information in an accessible, understandable manner. Bear in mind the need to translate technical language into layman's terms wherever possible, and to prioritize the main findings, implications, and novelty of the work."},
            {"role": "user",
             "content": f"Here is a scientific paper that requires your expertise for short and clear summary, 5 uniqe bullet points, and the top 5 relevant keywords: {text}"}
        ]
    )
    return ''.join(chunk["choices"][0]["delta"]["content"] for chunk in response if "content" in chunk["choices"][0]["delta"])


def fetch_and_save_articles(keyword="Brain", n=10, save_directory="saved_articles"):
    create_directory(save_directory)
    saved_filenames = set(os.listdir(save_directory))
    search = arxiv.Search(query=keyword, max_results=n, sort_by=arxiv.SortCriterion.SubmittedDate)

    # DataFrame for new articles
    df_new = pd.DataFrame(columns=["title", "summary", "url", "embedding"])

    for result in search.results():
        filename = sanitize_filename(result.title) + ".txt"
        if filename not in saved_filenames:
            text = sanitize_article_text(download_article_pdf(result.pdf_url))
            save_article(os.path.join(save_directory, filename), text)
            summary = summarize_article(text)
            article_data = {"title": result.title, "summary": summary, "url": result.entry_id, "embedding": ''}

            # Append the article data to df_new using pd.concat
            df_new = pd.concat([df_new, pd.DataFrame([article_data])], ignore_index=True)

            save_article(os.path.join(save_directory, filename.replace(".txt", "_summary.txt")), summary)

    # Load existing articles
    df_old = pd.read_csv("summary_embeddings.csv") if os.path.exists("summary_embeddings.csv") else pd.DataFrame(
        columns=["title", "summary", "url", "embedding"])

    # Combine old and new articles
    df_combined = pd.concat([df_new, df_old], ignore_index=True)
    df_combined.to_csv("summary_embeddings.csv", index=False)

    # Rerun the Streamlit app to refresh the view
    st.experimental_rerun()

def load_articles():
    print("Loading articles from CSV...")
    return pd.read_csv('summary_embeddings.csv')

st.title("Neuroscience Articles")

# Input controls for the user
keyword = st.sidebar.text_input("Search Keyword", "Brain")
n = st.sidebar.number_input("Number of articles", min_value=1, value=5)

if st.sidebar.button("Fetch New Articles"):
    fetch_and_save_articles(keyword, n)
    articles_data = load_articles()  # Refresh articles_data after fetching
    st.write("New articles fetched and saved!")

def fetch_articles_periodically(interval=3600):
    while True:
        fetch_and_save_articles(keyword, n)
        time.sleep(interval)


# if st.sidebar.checkbox('Enable Periodic Article Fetching'):
#     threading.Thread(target=fetch_articles_periodically).start()
articles_data = load_articles()


# Decide on display type (Expander vs Cards)
use_cards = st.sidebar.toggle('Display using cards', value=False)

# Display using expanders
if not use_cards:
    for index, row in articles_data.iterrows():
        with st.expander(row['title']):
            st.write(row['summary'])
else:
    card_style = """
    <style>
        .card {
            border: 1px solid #ddd;
            border-radius: 25px;
            padding: 20px;
            margin: 10px 0px;
            box-shadow: 5px 5px 5px grey;
        }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)
    for index, row in articles_data.iterrows():
        st.markdown(f"<div class='card'><h3>{row['title']}</h3><p>{row['summary']}</p></div>", unsafe_allow_html=True)


