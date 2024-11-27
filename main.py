import streamlit as st
import zipfile
from openai import OpenAI

st.header("WhatsApp Chat Summarizer")
[c1, c2] = st.columns([1, 1])
with c1:
    st.image("./logo.jpeg")
button = None

with c2:
    file = st.file_uploader(
        "Upload a file", type=["zip", "txt"], accept_multiple_files=False
    )
    checkpoint = st.text_input("Enter checkpoint text")
    api_key = st.text_input("OpenAI API Key (Optional)")
    button = st.button("Process")
openai = OpenAI(api_key=api_key if len(api_key)
                else st.secrets.get("OPENAI_API_KEY"))
if button and file is not None:
    if file.type == "application/zip":
        with zipfile.ZipFile(file) as z:
            for filename in z.namelist():
                if filename.endswith(".txt"):
                    with z.open(filename) as f:
                        content = f.read().decode("utf-8")
                    break
            else:
                st.error("No txt file found in the zip archive.")
                content = None
    else:
        content = file.getvalue().decode("utf-8")
    if content:

        # Extract chat context from checkpoint
        index = content.lower().find(checkpoint.lower())
        if index != -1:
            chat_context = content[index:]
        else:
            st.error("Checkpoint text not found in the file.")
            st.stop()
        # Prepare prompt for OpenAI API
        system_prompt = """You are an AI assistant that scans WhatsApp chats, summarises them, provides additional technical or external real world context and remove misinformation.
            "Note that the people involved in the conversation may not be subject matter experts.
            You are to enrich given conversation, to be be saved for later retrieval and give output in markdown format. Remove slurs and feel free to mention names of people in chat if available, don't include mobile numbers"""
        user_prompt = "Here's the conversation:\n\n" + chat_context
        with st.expander("See Extracted Chat Context"):
            st.header("System Prompt")
            st.markdown(system_prompt)
            st.header("Chat Context")
            st.markdown(chat_context)

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # max_tokens=1500
        )

        summary = response.choices[0].message.content
        # Display the output in markdown
        st.markdown(summary)
