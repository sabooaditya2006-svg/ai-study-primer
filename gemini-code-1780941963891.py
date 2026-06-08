import streamlit as st
from google import genai
from google.genai import types
import pypdf
import io

# Setup Streamlit page configuration to use full display width
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

# --- TOP STRIP: Website Name Banner ---
st.markdown(
    """
    <div style="background-color:#4A90E2;padding:10px;border-radius:10px;margin-bottom:20px;">
    <h2 style="color:white;text-align:center;margin:0;font-family:sans-serif;">🚀 SYNAPSE STUDY HUB</h2>
    </div>
    """, 
    unsafe_allow_html=True
)

if "pinned_bot_answer" not in st.session_state:
    st.session_state.pinned_bot_answer = ""

# Left Sidebar for master material file upload
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

# --- MAIN TWO-COLUMN SPLIT LAYER ---
col1, col2 = st.columns([32, 18], gap="large")

# =====================================================================
# LEFT COLUMN: MAIN STUDY AREA
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
        st.info("👈 Please upload a master PDF file in the left sidebar to get started!")

# =====================================================================
# RIGHT COLUMN: MULTITASKING SIDEBAR (Omni-Directional Scaling)
# =====================================================================
with col2:
    st.subheader("🛠️ Multitasking Sidebar")
    
    with st.expander("📺 Live Class Stream Window", expanded=True):
        
        screencast_html = """
        <div style="text-align: left; font-family: sans-serif; position: relative;">
            
            <div id="resizableContainer" style="position: relative; width: 100%; height: 260px; min-height: 120px; max-height: 700px; border: 2px dashed #4A90E2; border-radius: 8px; background-color: #111; display: flex; align-items: center; justify-content: center; box-sizing: border-box; touch-action: none; overflow: hidden;">
                
                <video id="videoElement" autoplay playsinline style="width: 100%; height: 100%; object-fit: fill; display: none; margin: 0; padding: 0; border: none;"></video>
                
                <button id="startBtn" style="background: none; border: none; color: #4A90E2; font-size: 56px; line-height: 1; cursor: pointer; font-weight: 300; outline: none; transition: transform 0.2s ease;">+</button>
                <button id="stopBtn" style="position: absolute; top: 10px; right: 10px; background: rgba(0, 0, 0, 0.6); color: white; border: none; border-radius: 50%; width: 26px; height: 26px; font-size: 16px; font-weight: bold; line-height: 24px; text-align: center; cursor: pointer; display: none; z-index: 99; outline: none; align-items: center; justify-content: center;">&times;</button>
                
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/interactjs/dist/interact.min.js"></script>
        
        <script>
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            const videoElement = document.getElementById('videoElement');
            const container = document.getElementById('resizableContainer');
            let currentStream = null;

            // Tight wrapper sync with Streamlit frame container boundary
            function syncStreamlitHeight() {
                const height = container.offsetHeight + 15;
                window.parent.postMessage({
                    type: 'streamlit:setFrameHeight',
                    height: height
                }, '*');
            }

            // Locked-position scaling (Only right and bottom drag anchors enabled)
            interact('#resizableContainer').resizable({
                edges: { right: true, bottom: true },
                listeners: {
                    move (event) {
                        // Apply dimensions directly to change size natively without translations
                        Object.assign(event.target.style, {
                            width: `${event.rect.width}px`,
                            height: `${event.rect.height}px`
                        });
                        syncStreamlitHeight();
                    }
                },
                modifiers: [
                    interact.modifiers.restrictSize({
                        min: { width: 180, height: 120 },
                        max: { width: 800, height: 700 }
                    })
                ],
                inertia: false
            });

            // Micro-feedback configurations
            startBtn.addEventListener('mouseenter', () => startBtn.style.transform = 'scale(1.15)');
            startBtn.addEventListener('mouseleave', () => startBtn.style.transform = 'scale(1)');

            startBtn.addEventListener('click', async () => {
                try {
                    currentStream = await navigator.mediaDevices.getDisplayMedia({
                        video: { cursor: "always" },
                        audio: false
                    });
                    videoElement.srcObject = currentStream;
                    videoElement.style.display = "block";
                    startBtn.style.display = "none";
                    stopBtn.style.display = "flex";
                    container.style.borderStyle = "solid";
                    syncStreamlitHeight();
                    
                    currentStream.getVideoTracks()[0].addEventListener('ended', () => {
                        clearStream();
                    });
                } catch (err) {
                    console.error("Capture selection context terminated: " + err);
                }
            });

            stopBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                clearStream();
            });

            function clearStream() {
                if (currentStream) {
                    currentStream.getTracks().forEach(track => track.stop());
                }
                videoElement.srcObject = null;
                videoElement.style.display = "none";
                stopBtn.style.display = "none";
                startBtn.style.display = "block";
                container.style.borderStyle = "dashed";
                currentStream = null;
                
                container.style.width = "100%";
                container.style.height = "260px";
                syncStreamlitHeight();
            }

            setTimeout(syncStreamlitHeight, 400);
        </script>
        """
        st.components.v1.html(screencast_html, height=280)

    # -----------------------------------------------------------------
    # COMPONENT 2: INTERACTIVE CHAT & HOMEWORK SCANNER
    # -----------------------------------------------------------------
    with st.expander("💬 Question & Assignment Scanner", expanded=True):
        if "document_text" in st.session_state and st.session_state.get("deep_dive") == True:
            st.markdown("📂 **Homework Scan Checker**")
            student_work_file = st.file_uploader("Upload your work (PDF) to check correctness", type=["pdf"], key="checker_uploader")
            
            student_work_text = ""
            if student_work_file:
                with st.spinner("Parsing submitted work sheets..."):
                    student_work_text = extract_text_from_pdf(student_work_file)
                st.info("⚡ Assignment verified. Type 'Check my homework' below to initiate scanning parameters.")

            chat_container = st.container(height=380)
            for idx, message in enumerate(st.session_state.chat_history):
                with chat_container.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if message["role"] == "assistant":
                        if st.button(f"📌 Send to Main Area", key=f"pin_{idx}"):
                            st.session_state.pinned_bot_answer = message["content"]
                            st.toast("Insight piped successfully to the Pinned Insights tab!")
                            st.rerun()
                    
            if user_query := st.chat_input("Ask a question or request grading evaluation..."):
                with chat_container.chat_message("user"):
                    st.markdown(user_query)
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                
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
                    with st.spinner("Processing analysis blocks..."):
                        client_response = client.models.generate_content(model='gemini-2.5-flash', contents=chat_prompt)
                        st.markdown(client_response.text)
                
                st.session_state.chat_history.append({"role": "assistant", "content": client_response.text})
                st.rerun()
        else:
            st.info("🔒 This portal automatically activates after clicking the main 'Generate Study Guides' trigger on your left.")
