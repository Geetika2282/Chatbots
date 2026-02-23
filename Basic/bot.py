import streamlit as st
import ollama

st.set_page_config(page_title="Ollama Chatbot")
st.title("Local Ollama Chatbot")

# chat memory
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Initialize conversation 
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "system", "content": "You are a helpful assistant. Give short, direct responses without any extra explanation unless asked. You are a precise assistant. Always solve math step by step before giving final answer. Never guess."}
    ]

inp = st.text_input("You: ", key="user")

if st.button("Send"):
    if inp.strip():
        st.session_state.conversation_history.append(
            {"role": "user", "content": inp})
        
        # include summary if exists
        messages_to_send = st.session_state.conversation_history.copy()

        # if summary exists
        if st.session_state.summary:
            messages_to_send.append({"role": "system", "content": f"Conversation summary: {st.session_state.summary}"})
    
        with st.spinner("Thinking..."):
            response = ollama.chat(
                model="gemma3:1b",
                messages=messages_to_send,
                options = {"num_predict": 50}   # limit response length 

            )

        reply = response["message"]["content"]
        st.session_state.conversation_history.append({
            "role": "assistant",
            "content": reply
        })

    # Summarize if long:
        if len(st.session_state.conversation_history) > 10: # change to 10
            convo_text = ""
            for m in st.session_state.conversation_history:
                convo_text += f"{m['role']}: {m['content']}\n"

            summary_prompt = f"""
            Summarize this conversation in short to use for chat memory: {convo_text}   
            """
            summary_response = ollama.chat(
                model = "gemma3:1b",
                messages=[{"role": "user", "content": summary_prompt}]
            )
            st.session_state.summary = summary_response["message"]["content"]
            st.session_state.conversation_history = [
                {"role": "system", "content": "You are a helpful assistant."},
            ] + st.session_state.conversation_history[-4:] # keep last 4 messages for context



# display
for msg in st.session_state.conversation_history[1:]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Bot:** {msg['content']}")