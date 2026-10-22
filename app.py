import streamlit as st
from dotenv import load_dotenv
import time
from datetime import datetime
import base64
import streamlit.components.v1 as components
import fitz  # PyMuPDF
import random

load_dotenv()
from generate import generate_answer

# 1. Page Configuration
st.set_page_config(page_title="CS AI Assistant", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# 2. Premium Professional CSS
st.markdown("""
<style>
    /* Transparent Header */
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }
    
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1e293b 0%, #0f172a 50%, #0b1120 100%) !important;
        color: #f8fafc !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 1200px !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #0f172a !important; border-right: 1px solid #1e293b; min-width: 320px !important; max-width: 320px !important; }

    /* Chat Messages */
    [data-testid="stChatMessage"] { padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 1px solid #1e293b; }
    [data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) { background-color: #1e293b; }
    [data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) { background-color: #0f172a; border-left: 4px solid #3b82f6; }
    
    /* Chat Input */
    [data-testid="stChatInput"] { background-color: #0f172a !important; border: 1px solid #3b82f6 !important; border-radius: 12px !important; box-shadow: 0 0 15px rgba(59, 130, 246, 0.15) !important; padding: 5px !important; }
    [data-testid="stChatInput"] textarea { background-color: transparent !important; color: #f8fafc !important; caret-color: #3b82f6 !important; }
    
    /* Sources */
    .source-box { background-color: rgba(30, 41, 59, 0.9); border-left: 3px solid #3b82f6; padding: 6px 12px; border-radius: 4px; margin-top: 8px; font-size: 0.8em; display: inline-block; margin-right: 6px; color: #94a3b8; }
    .timestamp { font-size: 0.7em; color: #64748b; margin-bottom: 8px; font-family: monospace; text-transform: uppercase; }

    /* Buttons */
    .stButton>button { background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #334155 !important; border-radius: 8px !important; transition: all 0.2s ease !important; }
    .stButton>button:hover { border-color: #3b82f6 !important; color: #3b82f6 !important; }
    .primary-btn button { background-color: #3b82f6 !important; border: none !important; }
    .primary-btn button:hover { background-color: #2563eb !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# 3. Text to Speech with Pause/Stop Controls
def play_audio(text):
    # Create a clean, safe ID using only letters and numbers
    import hashlib
    unique_id = hashlib.md5(text.encode()).hexdigest()[:8]
    
    # Escape quotes and newlines so the JS doesn't break
    safe_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '')
    
    tts_js = f"""
    <div style="display: flex; gap: 8px; margin-top: 10px; font-family: sans-serif;">
        <button id="play_{unique_id}" onclick="playAudio()" style="background-color:#1e293b; color:#f8fafc; border:1px solid #334155; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:12px; display:flex; align-items:center; gap:5px;">▶️ Play</button>
        <button id="pause_{unique_id}" onclick="pauseAudio()" style="background-color:#1e293b; color:#f8fafc; border:1px solid #334155; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:12px; display:flex; align-items:center; gap:5px;">⏸️ Pause</button>
        <button id="stop_{unique_id}" onclick="stopAudio()" style="background-color:#1e293b; color:#ef4444; border:1px solid #334155; padding:6px 12px; border-radius:6px; cursor:pointer; font-size:12px; display:flex; align-items:center; gap:5px;">⏹️ Stop</button>
    </div>

    <script>
    var synth = window.speechSynthesis;
    var utterance = new SpeechSynthesisUtterance("{safe_text}");
    utterance.rate = 1.0;

    function playAudio() {{
        synth.cancel(); // Stop anything currently playing
        synth.speak(utterance);
    }}

    function pauseAudio() {{
        if (synth.speaking) {{
            if (synth.paused) {{
                synth.resume();
            }} else {{
                synth.pause();
            }}
        }}
    }}

    function stopAudio() {{
        synth.cancel();
    }}
    </script>
    """
    components.html(tts_js, height=55)
# 4. Initialize State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = None
if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None

# 5. Sidebar Layout
with st.sidebar:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://img.icons8.com/color/96/000000/brain--v1.png", width=40)
    with col2:
        st.markdown("<h3 style='margin:0; padding-top:5px;'>CS Assistant</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("✨ Start New Chat", use_container_width=True, key="btn_new_chat_unique"):
        st.session_state.messages = []
        st.session_state.uploaded_text = None
        st.session_state.uploaded_name = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**📚 Document Library**")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], label_visibility="collapsed", key="file_uploader_unique")
    
    if uploaded_file is not None:
        with st.spinner("Processing..."):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            st.session_state.uploaded_text = text
            st.session_state.uploaded_name = uploaded_file.name
            st.success(f"Loaded: {uploaded_file.name}")
            
    if st.session_state.uploaded_text:
        st.info("💡 Chatting with uploaded document.")
        
    st.markdown("---")
    st.markdown("**💡 Daily Inspiration**")
    
    quotes = [
        ("The only way to learn a new programming language is by writing programs in it.", "Dennis Ritchie"),
        ("Talk is cheap. Show me the code.", "Linus Torvalds"),
        ("First, solve the problem. Then, write the code.", "John Johnson")
    ]
    
    selected_quote, author = random.choice(quotes)
    
    st.markdown(
        f"""
        <div style="background-color: #0f172a; padding: 15px; border-radius: 8px; border-left: 3px solid #3b82f6; margin-bottom: 15px; width: 100%;">
            <p style="font-style: italic; color: #94a3b8; font-size: 0.85em; margin-bottom: 8px; line-height: 1.4;">
                "{selected_quote}"
            </p>
            <p style="color: #64748b; font-size: 0.75em; margin: 0; text-align: right; font-weight: 600;">
                — {author}
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("**⚙️ Configuration**")
    max_tokens = st.slider("Max Tokens", 50, 500, 150, key="slider_max_tokens_unique")
    temperature = st.slider("Temperature", 0.1, 1.0, 0.7, key="slider_temperature_unique")
    
    st.markdown("---")
    if st.button("📥 Download Chat Log", use_container_width=True, key="btn_download_unique"):
        if st.session_state.messages:
            chat_text = ""
            for msg in st.session_state.messages:
                chat_text += f"[{msg['time']}] {msg['role'].upper()}:\n{msg['content']}\n\n"
            b64 = base64.b64encode(chat_text.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="chat_log.txt" style="text-decoration:none;"><button style="width:100%; padding:10px; background-color:#10b981; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; margin-top:10px;">Save File</button></a>'
            st.markdown(href, unsafe_allow_html=True)

# 6. Main Interface
st.title("CS AI Assistant")
st.caption("Grounded in textbooks • Powered by Custom Transformer & Groq")

if len(st.session_state.messages) == 0:
    st.markdown("<h1 style='text-align: center; margin-top: 10vh; font-size: 3em;'>How can I help you today?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 50px;'>Select a topic below or ask your own question.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>📊</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin-top: 0;'>Data Science</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9em;'>\"What is data science and what skills are required?\"</p>", unsafe_allow_html=True)
            
    with col2:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>💻</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin-top: 0;'>Java Programming</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9em;'>\"Write a simple Java program to print Hello World.\"</p>", unsafe_allow_html=True)
            
    with col3:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>📄</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin-top: 0;'>Custom Document</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9em;'>Upload your own PDF in the sidebar and ask questions directly from it.</p>", unsafe_allow_html=True)

# 7. Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="timestamp">{message["time"]}</div>', unsafe_allow_html=True)
        st.markdown(message["content"])
        
        if "sources" in message and message["sources"]:
            for source in message["sources"]:
                st.markdown(f'<div class="source-box">📖 <b>{source["book_id"]}</b> | Page {source["page"]}</div>', unsafe_allow_html=True)
        
        if message["role"] == "assistant":
            play_audio(message["content"])

# 8. Input Area
if prompt := st.chat_input("Message CS Assistant...", key="chat_input_unique_final"):
    current_time = datetime.now().strftime("%I:%M %p")
    
    st.session_state.messages.append({"role": "user", "content": prompt, "time": current_time})
    with st.chat_message("user"):
        st.markdown(f'<div class="timestamp">{current_time}</div>', unsafe_allow_html=True)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st.markdown(f'<div class="timestamp">{current_time}</div>', unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        full_response = ""
        
        res = generate_answer(
            prompt, 
            uploaded_text=st.session_state.uploaded_text,
            max_new_tokens=max_tokens, 
            temperature=temperature
        )
        answer = res["answer"]
        
        for chunk in answer.split(" "):
            full_response += chunk + " "
            time.sleep(0.02)
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
        if res.get("sources"):
            for source in res["sources"]:
                st.markdown(f'<div class="source-box">📖 <b>{source["book_id"]}</b> | Page {source["page"]}</div>', unsafe_allow_html=True)
        elif res.get("insufficient_evidence"):
            st.warning("⚠️ No relevant sources found.")

        play_audio(answer)

    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer,
        "sources": res.get("sources", []),
        "time": current_time
    })