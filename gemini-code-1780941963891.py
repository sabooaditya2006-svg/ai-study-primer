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
        st.write("Click below to link a window. You can drag **ANY border or corner** to resize it perfectly like an image.")
        
        # Injecting Interact.js engine with explicit frame height auto-sync handlers
        screencast_html = """
        <div style="text-align: center; font-family: sans-serif; padding-bottom: 5px;">
            <div style="margin-bottom: 10px;">
                <button id="startBtn" style="background-color: #4A90E2; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; font-weight: bold;">Add Meet / Lecture Window</button>
                <button id="stopBtn" style="background-color: #D9534F; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; font-weight: bold; display: none;">Remove Window Frame</button>
            </div>
            
            <div id="resizableContainer" style="width: 100%; height: 260px; min-height: 120px; max-height: 700px; border: 2px dashed #4A90E2; border-radius: 8px; background-color: #111; display: inline-block; box-sizing: border-box; touch-action: none;">
                <video id="videoElement" autoplay playsinline style="width: 100%; height: 100%; object-fit: contain; display: none; margin: 0 auto;"></video>
                <div id="placeholderText" style="color: #999; padding-top: 100px; font-size: 14px;">No active window frame selected</div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/interactjs/dist/interact.min.js"></script>
        
        <script>
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            const videoElement = document.getElementById('videoElement');
            const placeholderText = document.getElementById('placeholderText');
            const container = document.getElementById('resizableContainer');
            let currentStream = null;

            // Function to dynamically sync the outer Streamlit iframe size with your drag movements
            function syncStreamlitHeight() {
                const height = container.offsetHeight + 65;
                window.parent.postMessage({
                    type: 'streamlit:setFrameHeight',
                    height: height
                }, '*');
            }

            // Initialize multi-edge tracking resizing logic
            interact('#resizableContainer').resizable({
                edges: { left: true, right: true, bottom: true, top: true },
                listeners: {
                    move (event) {
                        let { x, y } = event.target.dataset;
                        x = (parseFloat(x) || 0) + event.deltaRect.left;
                        y = (parseFloat(y) || 0) + event.deltaRect.top;

                        Object.assign(event.target.style, {
                            width: `${event.rect.width}px`,
                            height: `${event.rect.height}px`,
                            transform: `translate(${x}px, ${y}px)`
                        });

                        Object.assign(event.target.dataset, { x, y });
                        syncStreamlitHeight();
                    }
                },
                modifiers: [
                    interact.modifiers.restrictSize({
                        min: { width: 200, height: 120 },
                        max: { width: 800, height: 700 }
                    })
                ],
                inertia: false
            });

            startBtn.addEventListener('click', async () => {
                try {
                    currentStream = await navigator.mediaDevices.getDisplayMedia({
                        video: { cursor: "always" },
                        audio: false
                    });
                    videoElement.srcObject = currentStream;
                    videoElement.style.display = "block";
                    placeholderText.style.display = "none";
                    stopBtn.style.display = "inline-block";
                    startBtn.style.display = "none";
                    syncStreamlitHeight();
                    
                    currentStream.getVideoTracks()[0].addEventListener('ended', () => {
                        clearStream();
                    });
                } catch (err) {
                    console.error("Error capturing workspace setup: " + err);
                }
            });

            stopBtn.addEventListener('click', () => {
                clearStream();
            });

            function clearStream() {
                if (currentStream) {
                    currentStream.getTracks().forEach(track => track.stop());
                }
                videoElement.srcObject = null;
                videoElement.style.display = "none";
                placeholderText.style.display = "block";
                stopBtn.style.display = "none";
                startBtn.style.display = "inline-block";
                currentStream = null;
                
                // Reset to default sizing profile on removal
                container.style.width = "100%";
                container.style.height = "260px";
                container.style.transform = "none";
                container.dataset.x = 0;
                container.dataset.y = 0;
                syncStreamlitHeight();
            }

            // Initial frame calculation load trigger
            setTimeout(syncStreamlitHeight, 500);
        </script>
        """
        # We replace the static height limit with a flexible starting envelope
        st.components.v1.html(screencast_html, height=340)

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
