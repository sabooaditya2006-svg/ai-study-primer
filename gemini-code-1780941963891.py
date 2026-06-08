import streamlit as st
from google import genai
from google.genai import types
import pypdf
import io

# Setup Streamlit page configuration
st.set_page_config(page_title="AI Study Primer", page_icon="📚", layout="wide")

# Initialize Gemini Client
try:
    client = genai.Client()
except Exception as e:
    st.error("Please set your GEMINI_API_KEY environment variable in Streamlit Secrets.")

# Helper function to extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

# Main UI Configuration
st.title("📚 AI Material Primer & Deep-Dive Assistant")
st.subheader("Prime your brain before you dive deep.")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF lecture/textbook", type=["pdf"])
    
    if uploaded_file:
        # TRACKING FILE CHANGES: If a new file is uploaded, wipe the old data instantly
        if "current_file_name" not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("Processing new document..."):
                st.session_state.document_text = extract_text_from_pdf(uploaded_file)
                st.session_state.current_file_name = uploaded_file.name
                # Reset all states for the new file
                st.session_state.primed = False
                st.session_state.deep_dive = False
                st.session_state.primer_output = ""
                st.session_state.deep_output = ""
                st.session_state.chat_history = []
        st.success(f"Active: {uploaded_file.name}")

# Layout split: Left side for study materials, Right side for Interactive Q&A
col1, col2 = st.columns([3, 2])

with col1:
    if "document_text" in st.session_state and st.session_state.document_text.strip() != "":
        st.header("📖 Study Materials")
        
        # Button to trigger processing using a single combined call to prevent server errors
        if st.button("Generate Study Guides", type="primary"):
            with st.spinner("Analyzing document and generating summaries..."):
                
                combined_prompt = (
                    "You are an expert educator. I am going to give you a text, and I need you to generate TWO distinct outputs. "
                    "You MUST separate the two outputs with the exact marker text: ---DEEP_DIVE_SPLIT---\n\n"
                    
                    "OUTPUT 1 (Before the marker): Provide a HIGH-LEVEL PRIMER. Focus on broad themes, the core 'Why does this matter?', "
                    "major vocabulary terms without dense definitions, and a mental roadmap. Keep it simple, bulleted, and highly scannable.\n\n"
                    
                    "OUTPUT 2 (After the marker): Provide an exhaustive, DEEP DIVE breakdown. Explain complex mechanisms, logical contexts, "
                    "and subtle nuances section by section with clear headings. Do not oversimplify.\n\n"
                    
                    f"Source Text:\n{st.session_state.document_text[:40000]}"
                )
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=combined_prompt,
                    )
                    
                    raw_text = response.text
                    # Split the single response text using our marker to separate the tabs
                    if "---DEEP_DIVE_SPLIT---" in raw_text:
                        parts = raw_text.split("---DEEP_DIVE_SPLIT---")
                        st.session_state.primer_output = parts[0].strip()
                        st.session_state.deep_output = parts[1].strip()
                    else:
                        st.session_state.primer_output = raw_text
                        st.session_state.deep_output = "The model forgot to separate the deep dive. You can find the entire response in the first tab or click generate again."
                    
                    st.session_state.primed = True
                    st.session_state.deep_dive = True
                    
                except Exception as e:
                    st.error("Google's free tier servers are currently busy. Please wait 10 seconds and click 'Generate Study Guides' again.")
                    st.session_state.primed = False
                    st.session_state.deep_dive = False

        # Display tabs if content has been generated successfully
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
    
    # UNLOCKED CHECK: Checks if a file is uploaded AND the deep dive processing is complete
    if "document_text" in st.session_state and st.session_state.get("deep_dive") == True:
        st.write("Ask anything about the text. Challenge assumptions, ask for analogies, or request further clarification.")
        
        # Container to display chat messages
        chat_container = st.container(height=500)
        for message in st.session_state.chat_history:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Chat input field
        if user_query := st.chat_input("What part don't you understand?"):
            with chat_container.chat_message("user"):
                st.markdown(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            chat_prompt = (
                "You are an interactive tutor helping a student understand their course material. "
                "Answer the student's question accurately using the provided source text as your primary truth. "
                "If they ask for analogies or simplified concepts, provide them, but keep the technical accuracy intact.\n\n"
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
        st.info("The chat interface will unlock once you click 'Generate Study Guides' and your materials are ready.")
