import streamlit as st
from datahandler import write_last_shows_to_memory, read_last_shows_from_memory


st.set_page_config(page_title="VK Videos", layout="wide")

if st.sidebar.button("Update"):
    write_last_shows_to_memory()

st.title("VK Videos")

shows = read_last_shows_from_memory()

for data in shows.values():
    date = data[0]['date']
    title = data[0]['title']
    url = data[0]['url']
    
    st.write(f"{date} | [{title}]({url})")
