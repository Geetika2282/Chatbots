import streamlit as st
import ollama

st.set_page_config(page_title="Local Ollama Chatbot")

st.title("Local Ollama Chatbot")
inp = st.text_input("You: ", key="user")

if st.button("Send"):
    if inp.strip() != "":
        with st.spinner("Thinking..."):
            response = ollama.chat(
                model="gemma3:1b",
                messages=[
                    {"role": "user", "content": inp}
                ]
            )

        st.markdown("### Response: ")
        st.write(response["message"]["content"])