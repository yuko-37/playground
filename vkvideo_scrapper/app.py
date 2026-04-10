import streamlit as st

from logger import configure_logging
from datahandler import write_last_shows_to_memory, read_last_shows_from_memory

configure_logging()

st.set_page_config(page_title="VK Videos", layout="wide")

if st.sidebar.button("Update"):
    write_last_shows_to_memory()

st.title("VK Videos")

try:
    shows = read_last_shows_from_memory()
except FileNotFoundError:
    st.info("No data yet. Click **Update** in the sidebar to fetch videos.")
    shows = {}

for data in shows.values():
    date = data[0]['date']
    title = data[0]['title']
    url = data[0]['url']

    st.write(f"{date} | [{title}]({url})")
