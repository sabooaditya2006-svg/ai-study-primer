import streamlit as st
from google import genai
from google.genai import types
import pypdf
import io

# Setup Streamlit page configuration
st.set_page_config(page_title="AI Study Primer", page_icon="📚", layout="wide")

# 1. LIGHT/DARK MODE STATE & DESIGN INJECTION (Matching image_96462f.jpg & 8428938656597922300.jpeg)
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

# CSS Themes Mapping
THEMES = {
    "Light": {
        "bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "text": "#1E293B",
        "sidebar_bg": "#FFFFFF",
        "accent": "#6366F1",
        "border": "#E2E8F0",
        "banner_bg": "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)",
        "banner_text": "#FFFFFF",
        "chat_user_bg": "#EEF2FF",
        "chat_bot_bg": "#F1F5F9",
    },
    "Dark": {
        "bg": "#0F172A",
        "card_bg": "#1E293B",
        "text": "#F1F5F9",
        "sidebar_bg": "#0F172A",
        "accent": "#818CF8",
        "border": "#334155",
        "banner_bg": "linear-gradient(135deg, #312E81 0%, #4C1D95 100%)",
        "banner_text": "#F8FAFC",
        "chat_user_bg": "#312E81",
        "chat_bot_bg": "#334155",
    }
}

current_theme = THEMES[st.session_state.theme_mode]

# Custom CSS Injector to handle complete dashboard skinning
custom_style = f"""
<style>
    /* Global Background Override */
    .stApp {{
        background-color: {current_theme['bg']} !important;
        color: {current_theme['text']} !important;
    }}
    
    /* Sidebar Overhaul */
    [data-testid="stSidebar"] {{
        background-color: {current_theme['sidebar_bg']} !important;
        border-right: 1px solid {current_theme['border']} !important;
    }}
    
    /* Banner/Header Block styling */
    .dashboard-banner {{
        background: {current_theme['banner_bg']};
        color: {current_theme['banner_text']};
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
    }}
    
    /* Document Display Cards & Layout Blocks */
    .dashboard-card {{
        background-color: {current_theme['card_bg']};
        border: 1px solid {current_theme['border']};
        padding: 1.5rem;
        border-radius: 14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
    }}
    
    /* Input Styling Text Corrections */
    div[data-baseweb="input"] {{
        background-color: {current_theme['card_bg']} !important;
        color: {current_theme['text']} !important;
        border-radius: 8px !important;
    }}
    
    /* Target Markdown components globally for visibility transitions */
    .stMarkdown, p, h1, h2, h3, h4, span {{
        color: {current_theme['text']} !important;
    }}
    .dashboard-banner p, .dashboard-banner h1, .dashboard-banner h3 {{
        color: {current_theme['banner_text']} !important;
    }}
</style>
"""
st.html(custom_style)

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

# --- SIDEBAR INTERFACE ---
with st.sidebar:
    st.logo("https://img.icons8.com/fluent-solid/128/6366F1/education.png", icon_image="https://img.icons8.com/fluent-solid/128/6366F1/education.png")
    st.title("Coursue")
    
    st.caption("OVERVIEW")
    st.markdown("🔹 **Dashboard**")
    st.markdown("📁 Lessons")
    st.markdown("📝 Tasks")
    
    st.write("---")
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF lecture/textbook", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        if "current_file_name" not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("Processing new document..."):
                st.session_state.document_text = extract_text_from_pdf(uploaded_file)
                st.session_state.current_file_name = uploaded_file.name
                st.session_state.primed = False
                st.session_state.deep_dive = False
                st.session_state.primer_output = ""
                st.session_state.deep_output = ""
                st.session_state.chat_history = []
        st.success(f"Active: {uploaded_file.name}")
        
    st.write("---")
    
    # Theme Mode Selector Widget placed neatly at the bottom area of the sidebar
    st.caption("PREFERENCES")
    theme_selection = st.radio(
        "Interface Mode",
        options=["Light", "Dark"],
        index=["Light", "Dark"].index(st.session_state.theme_mode),
        horizontal=True
    )
    if theme_selection != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_selection
        st.rerun()

# --- MAIN DASHBOARD LAYOUT ---
# 3-Column setup matching dashboard layouts but completely removing the mentor block element
col1, col2 = st.columns([3, 2])

# Left/Center Workspace Section
with col1:
    # Large UI Styled Hero Banner
    st.html(f"""
    <div class="dashboard-banner">
        <h1>Sharpen Your Skills with AI Course Priming</h1>
        <h3>Prime your brain before you dive deep.</h3>
    </div>
    """)
    
    if "document_text" in st.session_state and st.session_state.document_text.strip() != "":
        st.subheader("📖 Study Materials")
        
        if st.button("Generate Study Guides", type="primary", use_container_width=True):
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

        if st.session_state.get("primed"):
            tab1, tab2 = st.tabs(["🚀 Broad Primer (Read First)", "🔬 Deep Dive (Read Second)"])
            
            with tab1:
                st.html(f'<div class="dashboard-card">')
                st.markdown("### 🧠 Mental Sandbox / High-Level Roadmap")
                st.markdown(st.session_state.primer_output)
                st.html('</div>')
                
            with tab2:
                st.html(f'<div class="dashboard-card">')
                st.markdown("### 🔎 Comprehensive Breakdown")
                st.markdown(st.session_state.deep_output)
                st.html('</div>')
    else:
        st.info("Please upload a PDF file in the sidebar menu panel to unpack your dashboard workspace insights.")

# Right Interactive Chat Workspace Column (Aligned clean panel look)
with col2:
    st.html(f'<div class="dashboard-card" style="height: 100%;">')
    st.subheader("💬 Question the Material")
    
    if "document_text" in st.session_state and st.session_state.get("deep_dive") == True:
        st.write("Ask anything about the text. Challenge assumptions or ask for descriptive intuitive analogies.")
        
        chat_container = st.container(height=480)
        for message in st.session_state.chat_history:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])
                
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
        st.info("The interactive AI tutoring assistant chat unlocks right here immediately after your materials generate.")
    st.html('</div>')
