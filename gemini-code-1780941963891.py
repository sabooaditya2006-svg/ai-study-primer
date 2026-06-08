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

# --- SECTION 1: TOP STRIP (Website Name Banner) ---
st.markdown(
    """
    <div style="background-color:#4A90E2;padding:10px;border-radius:10px;margin-bottom:20px;">
    <h2 style="color:white;text-align:center;margin:0;font-family:sans-serif;">🚀 SYNAPSE STUDY HUB</h2>
    </div>
    """, 
    unsafe_allow_html=True
)

# Initialize global session variables if they don't exist
if "pinned_bot_answer" not in st.session_state:
    st.session_state.pinned_bot_answer = ""

# Sidebar for master material file upload
with st.sidebar:
    st.header("Master Course Material")
    uploaded_file = st.file_uploader("Upload Master PDF (Lecture/Textbook)", type=["pdf"], key="master_uploader")
    
    if uploaded_file:
        if "current_file_name" not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            with st.spinner("Processing master document..."):
                st.session_state.document_text = extract_text_from_pdf(uploaded_file)
                st.session_state.current_file_name = uploaded_file.name
                st.session_state.primed = False
                st.session_state.deep_dive = False
                st.session_state.primer_output = ""
                st.session_state.deep_output = ""
                st.session_state.chat_history = []
        st.success(f"Active Master: {uploaded_file.name}")

# Layout split: Left side (Main Area), Right side (Multitasking Column)
col1, col2 = st.columns([3, 2], gap="large")

# =====================================================================
# LEFT COLUMN: MAIN STUDY AREA (Primer, Deep Dive, & Pinned Answers)
# =====================================================================
with col1:
    if "document_text" in st.session_state and st.session_state.document_text.strip() != "":
        st.header("📖 Study Materials")
        
        if st.button("✨ Generate Study Guides", type="primary", use_container_width=True):
            with st.spinner("Analyzing document and building your study templates..."):
                combined_prompt = (
                    "You are an expert educator. I am going to give you a text, and I need you to generate TWO distinct outputs. "
                    "You MUST separate the two outputs with the exact marker text: ---DEEP_DIVE_SPLIT---\n\n"
                    "OUTPUT 1 (Before the marker): Provide a HIGH-LEVEL PRIMER. Focus on broad themes, the core 'Why does this matter?', "
                    "major vocabulary terms without dense definitions, and a mental roadmap. Keep it simple, bulleted, and highly scannable.\n\n"
                    "OUTPUT 2 (After the marker): Provide an exhaustive, DEEP DIVE breakdown. Explain complex mechanisms, logical contexts, "
                    "and subtle nuances section by section with clear headings.\n\n"
                    f"Source Text:\n{st.session_state.document_text[:40000]}"
                )
                try:
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=combined_prompt)
                    raw_text = response.text
                    if "---DEEP_DIVE_SPLIT---" in raw_text:
                        parts = raw_text.split("---DEEP_DIVE_SPLIT---")
                        st.session_state.primer_output = parts[0].strip()
                        st.session_state.deep_output = parts[1].strip()
                    else:
                        st.session_state.primer_output = raw_text
                        st.session_state.deep_output = "The model forgot to separate the deep dive."
                    st.session_state.primed = True
                    st.session_state.deep_dive = True
                except Exception as e:
                    st.error("Google's free tier servers are busy. Please wait 10 seconds and click generate again.")

        # Display tabs including the new Pinned Presentation Tab
        if st.session_state.get("primed"):
            tab1, tab2, tab3 = st.tabs(["🚀 Broad Primer", "🔬 Deep Dive", "📌 Pinned Bot Insights"])
            
            with tab1:
                st.info("💡 **Goal:** Build a basic mental model of the text before trying to memorize data points.")
                st.markdown(st.session_state.primer_output)
                
            with tab2:
                st.success("🔬 **Goal:** Review the fine details, complex logic, and deep context.")
                st.markdown(st.session_state.deep_output)
                
            with tab3:
                st.warning("🎯 **Main Display Area:** This tab contains answers you pinned from the chat bot for deep reading.")
                if st.session_state.pinned_bot_answer:
                    st.markdown(st.session_state.pinned_bot_answer)
                else:
                    st.write("*No answers pinned yet. Use the chat bot on the right and click 'Send to Main Area' to present it here.*")
    else:
        st.info("👈 Please upload a master PDF file in the sidebar to get started!")

# =====================================================================
# RIGHT COLUMN: THREE-PART MULTITASKING ZONE
# =====================================================================
with col2:
    # Part 1: Small Name Strip (Already placed at the absolute top of the app)
    
    # Part 2: Live Window Streamer (HTML5 Video Element via iframe trick)
    st.subheader("📺 Live Class Stream")
    st.write("Click below to sync your Google Meet/Lecture window directly into your workspace view.")
    
    # Custom HTML/JS component that grabs your browser screen sharing feed and scales it dynamically
    screencast_html = """
    <div style="text-align: center; font-family: sans-serif;">
        <button id="startBtn" style="background-color: #4A90E2; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 14px;">Select Lecture/Meet Window</button>
        <video id="videoElement" autoplay playsinline style="width: 100%; max-height: 250px; margin-top: 10px; border: 2px solid #ccc; border-radius: 8px; background-color: black; display: none;"></video>
    </div>

    <script>
        const startBtn = document.getElementById('startBtn');
        const videoElement = document.getElementById('videoElement');

        startBtn.addEventListener('click', async () => {
            try {
                const mediaStream = await navigator.mediaDevices.getDisplayMedia({
                    video: { cursor: "always" },
                    audio: false
                });
                videoElement.srcObject = mediaStream;
                videoElement.style.display = "block";
                startBtn.style.display = "none";
            } catch (err) {
                console.error("Error capturing screen: " + err);
            }
        });
    </script>
    """
    st.components.v1.html(screencast_html, height=310)
    st.write("---")
    
    # Part 3: Interactive Chat + Homework Scanner
    st.subheader("💬 Question & Assignment Scanner")
    
    if "document_text" in st.session_state and st.session_state.get("deep_dive") == True:
        # Homework Checker Uploader
        st.markdown("📂 **Homework Scan Checker**")
        student_work_file = st.file_uploader("Upload your work (PDF) to check correctness against the master text", type=["pdf"], key="checker_uploader")
        
        student_work_text = ""
        if student_work_file:
            with st.spinner("Parsing your submitted work..."):
                student_work_text = extract_text_from_pdf(student_work_file)
            st.info("⚡ Homework parsed. Ask the bot below: *'Check my homework'* to process evaluation.")

        # Container to display chat messages cleanly
        chat_container = st.container(height=350)
        for idx, message in enumerate(st.session_state.chat_history):
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])
                # If it's an assistant response, give an option to pin it to the main left area
                if message["role"] == "assistant":
                    if st.button(f"📌 Send to Main Area", key=f"pin_{idx}"):
                        st.session_state.pinned_bot_answer = message["content"]
                        st.toast("Insight sent to 'Pinned Bot Insights' tab!")
                        st.rerun()
                
        # Chat input field
        if user_query := st.chat_input("Ask a question or type 'Check my homework'"):
            with chat_container.chat_message("user"):
                st.markdown(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
            # Construct a smart context prompt that alters itself if a user uploaded homework
            if student_work_text != "" and ("check" in user_query.lower() or "homework" in user_query.lower() or "correct" in user_query.lower()):
                chat_prompt = (
                    "You are a strict but helpful grading assistant.\n"
                    "1. Evaluate the student's submitted work based entirely on the truth found in the Master Source Text.\n"
                    "2. Cross-reference their steps, math derivations, concepts, or statements.\n"
                    "3. Point out exactly where they made a mistake, explain why it is wrong based on the master file, and provide the correct methodology.\n\n"
                    f"MASTER SOURCE TEXT CLARIFICATION:\n{st.session_state.document_text[:25000]}\n\n"
                    f"STUDENT'S SUBMITTED WORK RECOGNITION:\n{student_work_text[:15000]}\n\n"
                    "Provide a structured evaluation breakdown."
                )
            else:
                chat_prompt = (
                    "You are an interactive tutor helping a student understand their course material.\n"
                    "Answer the student's question accurately using the provided source text as your primary truth.\n\n"
                    f"Source Text Context:\n{st.session_state.document_text[:30000]}\n\n"
                    f"Student Question: {user_query}"
                )
            
            with chat_container.chat_message("assistant"):
                with st.spinner("Analyzing data frameworks..."):
                    chat_response = client.models.generate_content(model='gemini-2.5-flash', contents=chat_prompt)
                    st.markdown(chat_response.text)
            
            st.session_state.chat_history.append({"role": "assistant", "content": chat_response.text})
            st.rerun()
            
    else:
        st.info("🔒 The assignment scanner and chatbot will activate once your master study guides finish generating on the left.")
