import streamlit as st
import ollama

st.set_page_config(page_title="Local Ollama Chatbot")
st.title("Local Ollama Chatbot")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

inp = st.text_input("You: ", key="user")

if st.button("Send"):
    if inp.strip() != "":
        st.session_state.conversation_history.append(
            {"role": "user", "content": inp})
        with st.spinner("Thinking..."):
            response = ollama.chat(
                model="gemma3:1b",
                messages=st.session_state.conversation_history
            )

        reply = response["message"]["content"]

        st.session_state.conversation_history.append(
            {"role": "assistant", "content": reply}
        )

# Display chat history
for msg in st.session_state.conversation_history[1:]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")     