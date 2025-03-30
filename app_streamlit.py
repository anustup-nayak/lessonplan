import os
import streamlit as st
from dotenv import load_dotenv
import tempfile
import base64
import time
import re

# Load environment variables and set up page
load_dotenv()
st.set_page_config(
    page_title="Teacher Copilot", 
    page_icon="🧠",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Import controller with error handling
try:
    from content_generator import LessonPlanController, DocumentManager
    
    # Initialize controller in session state
    if 'controller' not in st.session_state:
        api_key = st.session_state.get('api_key', os.getenv("OPENAI_API_KEY"))
        st.session_state.controller = LessonPlanController(api_key=api_key)
        
        # Ensure document_manager exists
        if not hasattr(st.session_state.controller, 'document_manager'):
            st.session_state.controller.document_manager = DocumentManager(st.session_state.controller.config)
except ImportError as e:
    st.error(f"Failed to import required modules: {str(e)}")
    st.stop()

# Initialize session state for messages and content
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your Teacher Copilot. I can help you create math lesson plans and worksheets. What grade level are you teaching?"}
    ]

if 'content_display' not in st.session_state:
    st.session_state.content_display = {
        "type": "welcome",
        "content": "Select a grade level and topic to get started.",
        "metadata": {}
    }

# Add Copilot-style CSS with improved styling for a cleaner look
st.markdown("""
<style>
    /* GitHub Copilot-like styling */
    .main .block-container {
        max-width: 100%;
        padding-top: 0;
        padding-right: 0;
        padding-left: 0;
        padding-bottom: 0;
    }
    
    /* Header styling */
    .copilot-header {
        background-color: #f6f8fa;
        border-bottom: 1px solid #d0d7de;
        padding: 10px 16px;
        display: flex;
        align-items: center;
    }
    
    .copilot-title {
        font-size: 16px;
        font-weight: 600;
        margin: 0;
    }
    
    /* Two-panel layout */
    .main-container {
        display: flex;
        height: calc(100vh - 61px);
    }
    
    /* Chat panel */
    .chat-panel {
        width: 45%;
        border-right: 1px solid #d0d7de;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .chat-messages {
        flex-grow: 1;
        overflow-y: auto;
        padding: 16px;
        background-color: #f6f8fa;
    }
    
    .chat-message {
        padding: 12px 16px;
        margin-bottom: 16px;
        border-radius: 6px;
    }
    
    .user-message {
        background-color: #ffffff;
        border: 1px solid #d0d7de;
    }
    
    .assistant-message {
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        border-left: 3px solid #2da44e;
    }
    
    .chat-input {
        padding: 16px;
        border-top: 1px solid #d0d7de;
        background-color: #ffffff;
    }
    
    /* Preview panel */
    .preview-panel {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .preview-header {
        padding: 12px 16px;
        background-color: #f6f8fa;
        border-bottom: 1px solid #d0d7de;
        font-weight: 600;
    }
    
    .preview-content {
        flex-grow: 1;
        overflow-y: auto;
        padding: 16px;
        background-color: #ffffff;
    }
    
    /* Action buttons */
    .action-button {
        background-color: #2da44e;
        color: white;
        border: none;
        padding: 5px 16px;
        border-radius: 6px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Helper functions
def extract_grade_level(text):
    """Extract grade level from text."""
    grades = re.findall(r'grade\s*(\d+)|(\d+)(st|nd|rd|th)?\s*grade', text.lower())
    for match in grades:
        if match[0]:  # 'grade X' format
            return int(match[0])
        elif match[1]:  # 'Xth grade' format
            return int(match[1])
    return None

def create_download_link(content, filename, button_text):
    """Create a downloadable PDF button."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            # Generate PDF
            st.session_state.controller._generate_pdf(content, tmp_file.name)
            
            # Create download link
            with open(tmp_file.name, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                encoded = base64.b64encode(pdf_bytes).decode()
            
            # Remove temp file
            os.unlink(tmp_file.name)
            
            # Return HTML link
            return f'<a href="data:application/pdf;base64,{encoded}" download="{filename}" class="action-button">{button_text}</a>'
    except Exception as e:
        return f"Error creating download link: {str(e)}"

def process_user_message(message):
    """Process user message and determine action to take."""
    message_lower = message.lower()
    
    # Check for grade level
    grade_level = extract_grade_level(message)
    
    if grade_level:
        return "set_grade", {"grade": grade_level}
    
    # Check for topic selection
    if re.search(r'(?:topic|number)\s*\d+', message_lower) or "select topic" in message_lower:
        # Try to extract topic number
        topic_match = re.search(r'(?:topic|number)\s*(\d+)', message_lower)
        if topic_match:
            topic_num = int(topic_match.group(1)) - 1  # Convert to 0-indexed
            return "select_topic", {"topic_id": topic_num}
    
    # Check for generation requests
    if "create" in message_lower or "generate" in message_lower:
        if "lesson" in message_lower or "plan" in message_lower:
            # Extract duration if mentioned
            duration = "45 minutes"  # Default
            if "30" in message_lower:
                duration = "30 minutes"
            elif "60" in message_lower or "hour" in message_lower:
                duration = "60 minutes"
            
            return "generate_lesson", {"duration": duration}
        
        if "worksheet" in message_lower:
            # Extract difficulty if mentioned
            difficulty = "mixed"  # Default
            if "easy" in message_lower:
                difficulty = "easy"
            elif "medium" in message_lower:
                difficulty = "medium"
            elif "hard" in message_lower or "difficult" in message_lower:
                difficulty = "hard"
                
            return "generate_worksheet", {"difficulty": difficulty}
    
    # Check for topic research request
    if "topic" in message_lower and ("show" in message_lower or "list" in message_lower or "research" in message_lower):
        return "research_topics", {}
    
    # Default: general query
    return "general_query", {"query": message}

# Add callback to clear chat input after sending
def clear_chat_input():
    st.session_state.chat_input = ""

# Add function to add user message and get assistant response
def handle_user_input(user_message):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Process message to determine intent
    intent, params = process_user_message(user_message)
    
    # Based on intent, perform appropriate action
    if intent == "set_grade":
        grade = params["grade"]
        st.session_state.grade = grade
        
        # Research topics for this grade (will be implemented in next step)
        response = f"Great! I'll help you create materials for Grade {grade}. Would you like me to suggest some math topics suitable for this grade level?"
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    elif intent == "research_topics":
        # Will be implemented in next step
        response = "I'll research some topics for you. This will be implemented in the next step."
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    elif intent == "select_topic":
        # Will be implemented in next step
        response = "I'll select that topic for you. This will be implemented in the next step."
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    elif intent == "generate_lesson":
        # Will be implemented in next step
        duration = params.get("duration", "45 minutes")
        response = f"I'll generate a {duration} lesson plan for you. This will be implemented in the next step."
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    elif intent == "generate_worksheet":
        # Will be implemented in next step
        difficulty = params.get("difficulty", "mixed")
        response = f"I'll generate a {difficulty} difficulty worksheet for you. This will be implemented in the next step."
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    else:  # general_query
        # Default response
        response = "I'm here to help you create math lesson plans and worksheets. Would you like to tell me what grade level you're teaching?"
        st.session_state.messages.append({"role": "assistant", "content": response})

# Add Copilot header
st.markdown('<div class="copilot-header"><h1 class="copilot-title">🧠 Teacher Copilot</h1></div>', unsafe_allow_html=True)

# Main container with two panels
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Two-column layout
col1, col2 = st.columns([1, 1.2])

# Chat panel (left)
with col1:
    st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
    
    # Chat messages area
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    # Display chat messages
    for msg in st.session_state.messages:
        role_class = "user-message" if msg["role"] == "user" else "assistant-message"
        st.markdown(f'<div class="chat-message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input area
    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    
    chat_input = st.text_area(
        "Type your message here...", 
        key="chat_input",
        height=100
    )
    
    if st.button("Send", key="send_btn", on_click=clear_chat_input):
        if chat_input.strip():
            # Process user input
            handle_user_input(chat_input)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Content panel (right)
with col2:
    st.markdown('<div class="preview-panel">', unsafe_allow_html=True)
    
    # Content header
    preview_type = st.session_state.content_display["type"].capitalize().replace("_", " ")
    st.markdown(f'<div class="preview-header">{preview_type}</div>', unsafe_allow_html=True)
    
    # Content body
    st.markdown('<div class="preview-content">', unsafe_allow_html=True)
    
    # Display appropriate content based on type
    content_type = st.session_state.content_display["type"]
    content = st.session_state.content_display["content"]
    
    if content_type == "welcome":
        st.info(content)
        
        # API Key settings
        with st.expander("⚙️ Settings"):
            new_api_key = st.text_input("OpenAI API Key", type="password", key="api_key_input")
            if st.button("Save API Key"):
                if new_api_key:
                    st.session_state.api_key = new_api_key
                    st.session_state.controller.set_api_key(new_api_key)
                    st.success("API key saved successfully!")
    
    elif content_type == "lesson_plan":
        st.markdown("### Lesson Plan")
        st.markdown(content)
        
        # Add download button
        st.markdown(create_download_link(content, "lesson_plan.pdf", "📥 Download Lesson Plan"), unsafe_allow_html=True)
    
    elif content_type == "worksheet":
        st.markdown("### Worksheet")
        st.markdown(content)
        
        # Add download button
        st.markdown(create_download_link(content, "worksheet.pdf", "📥 Download Worksheet"), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for document upload (minimized by default)
with st.sidebar:
    st.title("Reference Documents")
    st.info("Upload reference documents to enhance generated content.")
    
    uploaded_file = st.file_uploader("Upload document", type=["pdf", "txt", "docx"])
    
    if uploaded_file:
        with st.spinner("Processing document..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                file_path = tmp_file.name
            
            doc_id = st.session_state.controller.document_manager.import_document(file_path)
            
            if not doc_id.startswith("Error"):
                st.success(f"Document uploaded: {uploaded_file.name}")
                
                if 'documents' not in st.session_state:
                    st.session_state.documents = []
                
                st.session_state.documents.append({"id": doc_id, "name": uploaded_file.name})
            else:
                st.error(f"Failed to upload: {doc_id}")
    
    # Show uploaded documents
    if 'documents' in st.session_state and st.session_state.documents:
        st.subheader("Uploaded Documents")
        
        for doc in st.session_state.documents:
            st.write(f"📄 {doc['name']}")