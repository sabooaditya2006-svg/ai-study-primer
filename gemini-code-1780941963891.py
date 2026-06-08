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
                    st.error("Server is busy. Please wait a moment and click generate again.")

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
# RIGHT COLUMN: MULTITASKING SIDEBAR (Borderless Auto-Scaling Video Window)
# =====================================================================
with col2:
    st.subheader("🛠️ Multitasking Sidebar")
    
    with st.expander("📺 Live Class Stream Window", expanded=True):
        
        # Single continuous line code block to completely bypass Python string parser syntax issues
        screencast_html = """<div style="text-align:left;font-family:sans-serif;position:relative;margin:0;padding:0;"><div id="liveWindowFrame" style="position:relative;width:100%;height:260px;min-height:140px;max-height:650px;border:2px dashed #4A90E2;border-radius:8px;background-color:#111;display:flex;align-items:center;justify-content:center;box-sizing:border-box;overflow:hidden;resize:both;"><video id="videoPlayer" autoplay playsinline style="width:100%;height:100%;object-fit:fill;display:none;margin:0;padding:0;pointer-events:none;"></video><button id="addStreamBtn" style="background:none;border:none;color:#4A90E2;font-size:64px;cursor:pointer;font-weight:300;outline:none;transition:transform 0.2s ease;">+</button><button id="closeStreamBtn" style="position:absolute;top:12px;right:12px;background:rgba(0,0,0,0.7);color:#fff;border:1px solid rgba(255,255,255,0.3);border-radius:50%;width:28px;height:28px;font-size:18px;line-height:24px;text-align:center;cursor:pointer;display:none;z-index:999;outline:none;align-items:center;justify-content:center;">&times;</button></div></div><script>const addStreamBtn=document.getElementById('addStreamBtn');const closeStreamBtn=document.getElementById('closeStreamBtn');const videoPlayer=document.getElementById('videoPlayer');const windowFrame=document.getElementById('liveWindowFrame');let streamInstance=null;function matchFrameHeight(){const currentHeight=windowFrame.offsetHeight+20;window.parent.postMessage({type:'streamlit:setFrameHeight',height:currentHeight},'*');}const resizeObserver=new ResizeObserver(()=>{matchFrameHeight();});resizeObserver.observe(windowFrame);addStreamBtn.addEventListener('click',async()=>{try{streamInstance=await navigator.mediaDevices.getDisplayMedia({video:{cursor:"always"},audio:false});videoPlayer.srcObject=streamInstance;videoPlayer.style.display="block";addStreamBtn.style.display="none";closeStreamBtn.style.display="flex";windowFrame.style.borderStyle="solid";matchFrameHeight();streamInstance.getVideoTracks()[0].addEventListener('ended',()=>{resetToDefault();});}catch(err){console.log("Stream canceled.");}});closeStreamBtn.addEventListener('click',(e)=>{e.stopPropagation();resetToDefault();});void function() { addStreamBtn.addEventListener('mouseenter',()=>addStreamBtn.style.transform='scale(1.2)'); addStreamBtn.addEventListener('mouseleave',()=>addStreamBtn.style.transform='scale(1)'); }();function resetToDefault(){if(streamInstance){streamInstance.getTracks().forEach(track=>track.stop());}videoPlayer.srcObject=null;videoPlayer.style.display="none";closeStreamBtn.style.display="none";addStreamBtn.style.display="block";windowFrame.style.borderStyle="dashed";streamInstance=null;windowFrame.style.width="100%";windowFrame.style.height="260px";matchFrameHeight();}window.addEventListener('load',()=>{setTimeout(matchFrameHeight,300);});</script>"""
        st.components.v1.html(screencast_html, height=285)

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
            
            # Formatted loops explicitly protecting indentation parameters from clipboard tearing
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
