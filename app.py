import streamlit as st
import streamlit.components.v1 as components

html_string = 'index.html' # load your HTML from disk here
st.components.v1.html(html_string)