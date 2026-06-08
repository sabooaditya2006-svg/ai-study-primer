import streamlit as st
from google import genai
from google.genai import types
import pypdf
import io

# Setup Streamlit page configuration
st.set_page_config(page_title="AI Study Primer", page_icon="📚", layout="wide")

# Initialize Gemini Client
# It automatically looks for an environment variable named GEMINI_API_KEY
# Or you can paste it directly: client = genai.Client(api_key="YOUR_KEY")
try:
    client = genai.Client()
except Exception as e:
    st.error("Please set your GEMINI_API_KEY environment variable.")

# Helper function to extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

# Main UI
st.title("📚 AI Material Primer & Deep-Dive Assistant")
st.subheader("Prime your brain before you dive deep.")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF lecture/textbook", type=["pdf"])
    
    if uploaded_file:
        st.success("File uploaded successfully!")
        
        # Extract text once and store it in session state
        if "document_text" not in st.session_state:
            with st.spinner("Extracting text from PDF..."):
                st.session_state.document_text = extract_text_from_pdf(uploaded_file)
                st.session_state.primed = False
                st.session_state.deep_dive = False
                st.session_state.chat_history = []

# Layout split: Left side for study materials, Right side for Interactive Q&A
col1, col2 = st.columns([3, 2])

with col1:
    if "document_text" in st.session_state:
        st.header("📖 Study Materials")
        
        # Button to trigger the processing
        if st.button("Generate Study Guides", type="primary"):
            with st.spinner("Analyzing document and generating summaries..."):
                
                # 1. Generate the Broad Primer
                primer_prompt = (
                    "You are an expert educator. Provide a HIGH-LEVEL PRIMER of the following text. "
                    "Your goal is to prepare the student's brain before they study deeply. "
                    "Focus on: Broad themes, the core 'Why does this matter?', major vocabulary terms without dense definitions, "
                    "and a mental roadmap of the material. Keep it incredibly simple, bulleted, and highly scannable."
                    f"\n\nText:\n{st.session_state.document_text[:40000]}" # Truncating slightly just to stay safe on basic text extraction
                )
                
                primer_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=primer_prompt,
                )
                st.session_state.primer_output = primer_response.text
                st.session_state.primed = True

                # 2. Generate the Deep Dive
                deep_prompt = (
                    "You are an expert educator. Provide an exhaustive, DEEP DIVE breakdown of the following text. "
                    "Explain complex mechanisms, mathematical derivations if any, historical/logical contexts, "
                    "and subtle nuances. Break it down section by section with clear headings. "
                    "Do not oversimplify; explain things thoroughly as if preparing someone for a rigorous exam."
                    f"\n\nText:\n{st.session_state.document_text[:40000]}"
                )
                
                deep_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=deep_prompt,
                )
                st.session_state.deep_output = deep_response.text
                st.session_state.deep_dive = True

        # Display tabs if content has been generated
        if st.session_state.get("primed"):
            tab1, tab2 = st.tabs(["🚀 Broad Primer (Read First)", "🔬 Deep Dive (Read Second)"])
            
            with tab1:
                st.markdown("### 🧠 Mental Sandbox / High-Level Roadmap")
                st.markdown(st.session_state.primer_output)
                
            with tab2:
                st.markdown("### 🔎 Comprehensive Breakdown")
                st.markdown(st.session_state.deep_output)
    else:
        st.info("Please upload a PDF file in the sidebar to begin.")

# Right Column: Interactive Chat Interface
with col2:
    st.header("💬 Question the Material")
    
    if "document_text" in st.session_state and st.session_state.get("deep_dive"):
        st.write("Ask anything about the text. Challenge assumptions, ask for analogies, or request further clarification.")
        
        # Container to display chat messages
        chat_container = st.container(height=500)
        for message in st.session_state.chat_history:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Chat input field
        if user_query := st.chat_input("What part don't you understand?"):
            # Display user message
            with chat_container.chat_message("user"):
                st.markdown(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Formulate prompt for the chat with the context of the document
            chat_prompt = (
                "You are an interactive tutor helping a student understand their course material. "
                "Answer the student's question accurately using the provided source text as your primary truth. "
                "If they ask for analogies or simplified physics/engineering concepts, provide them, but keep the technical accuracy intact.\n\n"
                f"Source Text Context:\n{st.session_state.document_text[:30000]}\n\n"
                f"Student Question: {user_query}"
            )
            
            with chat_container.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    chat_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=chat_prompt,
                    )
                    st.markdown(chat_response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": chat_response.text})
            
    else:
        st.info("The chat interface will unlock once you upload a document and generate the study guides.")
