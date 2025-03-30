"""
Teacher Copilot Anvil App

This application provides an AI-powered assistant for teachers to generate math lesson plans
and worksheets using a GitHub Copilot-like interface. It's built using the Anvil platform 
for web application development.

Key Features:
- Interactive chat interface for communicating with the AI assistant
- Grade-level specific content generation (grades 1-5)
- Curriculum-aligned topic suggestions based on selected grade level
- Detailed lesson plan generation with customizable duration (30, 45, or 60 minutes)
- Worksheet generation with adjustable difficulty levels (easy, medium, hard, or mixed)
- PDF export functionality for both lesson plans and worksheets
- Split-panel UI with chat on the left and content preview on the right

How It Works:
1. Teachers specify a grade level (1-5)
2. The app suggests grade-appropriate math topics
3. Teachers select a topic of interest
4. Teachers can generate a custom lesson plan
5. Teachers can generate an accompanying worksheet
6. Both the lesson plan and worksheet can be downloaded as PDFs

Technical Architecture:
- Client-side UI built with Anvil components
- Server-side processing for content generation
- Integration with LessonPlanController for the core functionality
- API integration for AI-powered content generation

To use this file:
1. Create a new Anvil app at https://anvil.works
2. Create a new module and paste this code
3. Set up the required dependencies and server functions
4. Configure API key(s) for the AI services
"""

# Client-side code for the Anvil app
import anvil.server
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import re
import anvil.media
import anvil.js

# Define the main form with a GitHub Copilot-like interface
class TeacherCopilotForm(Form):
  def __init__(self, **properties):
    # Initialize form
    self.init_components(**properties)
    
    # Initialize state
    self.messages = []
    self.content_type = "welcome"
    self.content_data = "Select a grade level and topic to get started"
    self.uploaded_documents = []
    
    # Add welcome message to the chat
    self.add_message("assistant", "Hi! I'm your Teacher Copilot. I can help you create math lesson plans and worksheets. What grade level are you teaching?")
    
    # Initial UI setup
    self.refresh_chat_panel()
    self.refresh_content_panel()
    
    # Set focus to chat input
    self.chat_input.focus()
  
  def init_components(self, **properties):
    # Call the Form's constructor
    super().__init__(**properties)
    
    # Set up the main layout components
    self.header_panel = FlowPanel(
      spacing_above="none",
      spacing_below="none",
      background="#f1f2f3",  # Updated to match GitHub Copilot header color
      border="0 0 1px 0 solid #d0d7de",
      padding=8
    )
    
    self.header_title = Label(
      text="Teacher Copilot",
      font_size=16,
      font_weight="bold",
      spacing_above="none",
      spacing_below="none"
    )
    
    # Add settings button to header
    self.settings_button = Button(
      text="⚙️",
      background="transparent",
      foreground="#57606a",  # GitHub text color for secondary actions
      border="none",
      icon_align="left"
    )
    
    self.header_panel.add_component(self.header_title)
    self.header_panel.add_component(self.settings_button)
    self.add_component(self.header_panel)
    
    # Main content column panel
    self.content_container = ColumnPanel(
      spacing_above="none",
      spacing_below="none",
      background="#ffffff"
    )
    
    # Two-panel layout using a Grid
    self.main_grid = GridPanel(
      spacing_above="none",
      spacing_below="none"
    )
    
    # Chat panel (left side)
    self.chat_panel = ColumnPanel(
      spacing_above="none",
      spacing_below="none",
      background="#f6f8fa",  # Matches GitHub Copilot's chat background
      border="0 1px 0 0 solid #d0d7de"
    )
    
    # Messages container
    self.chat_messages_container = LinearPanel(
      spacing_above="none",
      spacing_below="none",
      background="#f6f8fa",
      padding=16
    )
    
    # Chat input area
    self.chat_input_container = ColumnPanel(
      spacing_above="none",
      spacing_below="none",
    )# Configure input box and button
    (
    self.send_button = Button("Type your message here...",
      text="Send",,
      bold=True,
      background="#2da44e",
      foreground="#ffffff",
      width="fill"
    )self.send_button = Button(
    
    # Add input and button to container
    self.chat_input_container.add_component(self.chat_input)
    self.chat_input_container.add_component(self.send_button)  foreground="#ffffff",
    
    # Add message container and input container to chat panel
    self.chat_panel.add_component(self.chat_messages_container, width="stretch")
    self.chat_panel.add_component(self.chat_input_container)# Add input and button to container
    ent(self.chat_input)
    # Content preview panel (right side)ponent(self.send_button)
    self.content_panel = ColumnPanel(
      spacing_above="none", and input container to chat panel
      spacing_below="none",mponent(self.chat_messages_container, width="stretch")
      background="#ffffff"elf.chat_panel.add_component(self.chat_input_container)
    )
    w panel (right side)
    # Content header(
    self.content_header = FlowPanel(
      spacing_above="none",
      spacing_below="none",
      background="#f6f8fa",
      border="0 0 1px 0 solid #d0d7de",
      padding=12 Content header
    )self.content_header = FlowPanel(
    
    self.content_title = Label(none",
      text="Welcome",f6f8fa",
      font_size=14,olid #d0d7de",
      font_weight="bold",
      spacing_above="none",
      spacing_below="none"
    )self.content_title = Label(
    
    self.content_header.add_component(self.content_title)  font_size=14,
    "bold",
    # Content body
    self.content_body = ColumnPanel(
      spacing_above="none",
      spacing_below="none",
      background="#ffffff",_header.add_component(self.content_title)
      padding=16
    )# Content body
    el(
    self.content_text = RichText(
      content="Your generated content will appear here.",none",
      height="250px",
      spacing_above="none",
      spacing_below="none"
    )
    
    self.download_panel = FlowPanel( content will appear here.",
      spacing_above="medium",
      spacing_below="none",="none",
      visible=False spacing_below="none"
    ))
    
    self.download_button = Button(wPanel(
      text="📥 Download PDF",",
      background="#2da44e",,
      foreground="#ffffff" visible=False
    ))
    
    self.download_panel.add_component(self.download_button)self.download_button = Button(
    
    self.content_body.add_component(self.content_text)
    self.content_body.add_component(self.download_panel)  foreground="#ffffff"
    
    # Add header and body to content panel
    self.content_panel.add_component(self.content_header)
    self.content_panel.add_component(self.content_body, width="stretch")
    lf.content_text)
    # Add panels to grid - 40/60 split
    self.main_grid.add_component(self.chat_panel, row=0, col_xs=0, width_xs=12, col_md=0, width_md=5)
    self.main_grid.add_component(self.content_panel, row=0, col_xs=0, width_xs=12, col_md=5, width_md=7)  row="A", # Add header and body to content panel
    _header)
    # Add grid to main container")
    self.content_container.add_component(self.main_grid)  col_md=0,
    width on desktop40/60 split
    # Add container to formxs=12, col_md=0, width_md=5)
    self.add_component(self.content_container))self.main_grid.add_component(self.content_panel, row=0, col_xs=0, width_xs=12, col_md=5, width_md=7)
    onent(settings area
    # Set up event handlers
    self.send_button.set_event_handler("click", self.send_message_click)
    self.chat_input.set_event_handler("pressed_enter", self.send_message_enter)
    self.download_button.set_event_handler("click", self.download_content)    width_xs=12,  # Full width on mobile (under chat panel)  # Add container to form  )
  .content_container)
  # UI Helper methods
  def add_message(self, role, content, message_type="text"):
    """Add a message to the chat history.""" ColumnPanel(ht="bold"
    message = {
      "role": role,ntainer",
      "content": content,add_component(self.main_grid)d7de",Loader(
      "type": message_type,
      "id": str(len(self.messages)) Add container to form padding=16,
    }nt_container)
    self.messages.append(message)  height=300self.upload_button = Button(
    ndlers
    # Refresh chat UIt_handler("click", self.send_message_click)
    self.refresh_chat_panel()  self.chat_input.set_event_handler("pressed_enter", self.send_message_enter)  self.settings_title = Label(  )
  ent_handler("click", self.download_content)
  def refresh_chat_panel(self):elf.check_layout)
    """Update the chat panel with current messages."""abel)
    # Clear existing messages
    self.chat_messages_container.clear()"""Adjust layout based on screen size."""self.document_upload_panel.add_component(self.upload_button)
    th using JS = Label(text="OpenAI API Key:")
    # Add each messagennerWidthBox(
    for msg in self.messages:)
      # Create container for the messagebreakpoint
      msg_panel = ColumnPanel(ly on mobile
        spacing_above="none", "400px"  # Fixed height for chat on mobiled_message_click)
        spacing_below="small",ginning of row
        background="#ffffff" if msg["role"] == "user" else "#f6f8fa",tings["row"] = "B"   # Second rowclick", self.download_content)
        border="1px solid #d0d7de",
        border_left="3px solid " + ("#6c8ebf" if msg["role"] == "user" else "#82b366"),desktopf"
        border_radius=6,nel.height = "100%"    # Full heightontent, message_type="text"):
        padding=12elf.content_panel.layout_settings["col_md"] = 5  # Start after chat panel a message to the chat history."""
      )self.content_panel.layout_settings["row"] = "A"   # Same rowAdd components to settings panelssage = {
      ettings_title)
      # Add avatar infonent(self.api_key_label)
  def add_message(self, role, content, message_type="text"):
    """Add a message to the chat history."""role"] == "user" else "AI",_component(self.save_api_key_button)ssages))
    message = {bold",
      "role": role,
      "content": content,if msg["role"] == "user" else "#82b366",ettings_panel)
      "type": message_type, spacing_below="small"esh chat UI
      "id": str(len(self.messages)))Set up event handlerslf.refresh_chat_panel()
    }self.send_message_click)
    self.messages.append(message)dler("pressed_enter", self.send_message_enter):
    nt_handler("click", self.download_content)th current messages."""
    # Refresh chat UI],event_handler("click", self.toggle_settings)
    self.refresh_chat_panel(),.set_event_handler("click", self.save_api_key)iner.clear()
   spacing_below="none"
  def refresh_chat_panel(self):) Helper methodsAdd each message
    """Update the chat panel with current messages."""
    # Clear existing messages
    self.chat_messages_container.clear()
    msg_panel.add_component(message_text)"role": role,  spacing_above="none",
    # Add each message
    for msg in self.messages:
      # Create container for the message  self.chat_messages_container.add_component(msg_panel)  "id": str(len(self.messages))    border="1px solid #d0d7de",
      msg_panel = ColumnPanel(e"] == "user" else "#82b366"),
        spacing_above="none",
        spacing_below="small",  anvil.js.window.setTimeout(lambda: anvil.js.window.scrollTo(0, anvil.js.window.document.body.scrollHeight), 100)        padding=12
        background="#ffffff" if msg["role"] == "user" else "#f6f8fa",
        border="1px solid #d0d7de",
        border_left="3px solid " + ("#6c8ebf" if msg["role"] == "user" else "#82b366"),content panel based on current display type."""
        border_radius=6,
        padding=12self.content_title.text = self.content_type.capitalize()"""Update the chat panel with current messages."""    text="You" if msg["role"] == "user" else "AI",
      )
      
      # Add avatar info
      avatar_label = Label(elf.content_data}</p>"
        text="You" if msg["role"] == "user" else "AI",self.download_panel.visible = Falser msg in self.messages:)
        font_weight="bold",
        font_size=12,
        foreground="#6c8ebf" if msg["role"] == "user" else "#82b366",ntent_data
        spacing_below="small"self.download_panel.visible = False  spacing_below="small",  content=msg["content"],
      )
      
      # Add message contenter" else "#82b366"),
      message_text = RichText(wnload Lesson Plan"
      self.download_panel.visible = True  content=msg["content"],  padding=12if self.content_type == "lesson_plan":# Add components to message
      
    elif self.content_type == "worksheet":
      self.content_text.content = self.content_data
      self.download_button.text = "📥 Download Worksheet"
      self.download_panel.visible = True    # Add components to message      text="You" if msg["role"] == "user" else "AI",    self.download_button.text = "📥 Download Lesson Plan"    self.chat_messages_container.add_component(msg_panel)
  
  def set_content(self, content_type, content_data):
    """Set the content to display in preview panel."""6",heet":a: anvil.js.window.scrollTo(0, anvil.js.window.document.body.scrollHeight), 100)
    self.content_type = content_type
    self.content_data = content_dataer.add_component(msg_panel)
    self.refresh_content_panel()          html_content = self._markdown_to_html(markdown_content)  """Update the content panel based on current display type."""
  ttome content_text.content = html_content
  # Event handlersjs.window.scrollTo(0, anvil.js.window.document.body.scrollHeight), 100)capitalize()
  def send_message_click(self, **event_args):
    """Handle the send button click."""f):
    self.process_user_message()  """Update the content panel based on current display type."""      spacing_below="none"def _markdown_to_html(self, markdown_text):  if self.content_type == "welcome":
  
  def send_message_enter(self, **event_args):italize()
    """Handle pressing Enter in the input field."""
    self.process_user_message()  # Update content based on type    msg_panel.add_component(avatar_label)    elif self.content_type == "topics":
  ome":sage_text)
  def process_user_message(self):data}</p>"
    """Process user message and generate response."""e.MULTILINE)
    message = self.chat_input.text.strip()er.add_component(msg_panel)'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)nt_type == "lesson_plan":
    if not message:f.content_type == "topics":ent = self.content_data
      return  self.content_text.content = self.content_data# Scroll to bottom# Bold  self.download_button.text = "📥 Download Lesson Plan"
    ble = False(lambda: anvil.js.window.scrollTo(0, anvil.js.window.document.body.scrollHeight), 100)*\*', r'<strong>\1</strong>', html)ble = True
    # Add user message to chat
    self.add_message("user", message)elif self.content_type == "lesson_plan":f refresh_content_panel(self):# Italicelif self.content_type == "worksheet":
    t_text.content = self.content_data content panel based on current display type."""(r'\*(.+?)\*', r'<em>\1</em>', html)t_text.content = self.content_data
    # Clear inputxt = "📥 Download Lesson Plan"
    self.chat_input.text = ""  self.download_panel.visible = Trueself.content_title.text = self.content_type.capitalize()# Lists  self.download_panel.visible = True
    
    # Process message to determine intentINE)):
    intent, params = self.analyze_message(message)  self.content_text.content = self.content_dataif self.content_type == "welcome":"""Set the content to display in preview panel."""
    ext = "📥 Download Worksheet"ent = f"<p>{self.content_data}</p>"_type
    # Show loading indicator
    loading_notification = anvil.Notification("Processing your request...", timeout=None, style="success")
    loading_notification.show()f set_content(self, content_type, content_data):elif self.content_type == "topics":return html
    et the content to display in preview panel."""lf.content_text.content = self.content_datalers
    try: = content_typeanel.visible = Falsef, content_type, content_data):ick(self, **event_args):
      # Handle intent_datack."""
      if intent == "set_grade":
        self.handle_grade_selection(params["grade"])nt_data = content_datalf.content_text.content = self.content_data
        
      elif intent == "research_topics":nt_args):
        self.handle_topic_research()andle the send button click."""t handlersrocess_user_message()
        gs):heet":
      elif intent == "select_topic":
        self.handle_topic_selection(params["topic_id"])nd_message_enter(self, **event_args):.process_user_message()lf.download_button.text = "📥 Download Worksheet"rocess user message and generate response."""
        ut field."""
      elif intent == "generate_lesson":
        self.handle_lesson_generation(params.get("duration", "45 minutes"))pressing Enter in the input field."""t_content(self, content_type, content_data):turn
        
      elif intent == "generate_worksheet":
        self.handle_worksheet_generation(params.get("difficulty", "mixed"))age = self.chat_input.text.strip()ocess_user_message(self):.content_data = content_dataadd_message("user", message)
        ate response."""el()
      elif intent == "help":
        self.handle_help_request()essage:t handlers.chat_input.text = ""
        at:
      else:  # general querye)
        self.handle_general_query()# Add user message to chatself.process_user_message()intent, params = self.analyze_message(message)
    input_message("user", message)
    finally:
      # Hide loading indicator.", timeout=None, style="success")
      loading_notification.dismiss()  # Process message to determine intent  self.chat_input.text = ""  self.process_user_message()  loading_notification.show()
  sage(message)
  def analyze_message(self, message):
    """Analyze user message to determine intent."""onse."""
    # Convert to lowercase for comparisontification("Processing your request...", timeout=None, style="success")
    message_lower = message.lower()loading_notification.show()# Show loading indicatorif not message:    self.handle_grade_selection(params["grade"])
    cessing your request...", timeout=None, style="success")
    # Check for grade level
    grade_match = re.search(r'grade\s*(\d+)|(\d+)(st|nd|rd|th)?\s*grade', message_lower)ntic_research()
    if grade_match:
      grade = int(grade_match.group(1) or grade_match.group(2))["grade"])
      return "set_grade", {"grade": grade}      if intent == "set_grade":# Clear input    self.handle_topic_selection(params["topic_id"])
    :rams["grade"])
    # Check for topic selection intent
    if re.search(r'(?:topic|number)\s*(\d+)', message_lower):
      topic_match = re.search(r'(?:topic|number)\s*(\d+)', message_lower)
      topic_num = int(topic_match.group(1)) - 1"])
      return "select_topic", {"topic_id": topic_num}      elif intent == "select_topic":# Show loading indicator    self.handle_worksheet_generation(params.get("difficulty", "mixed"))
    sson":on(params["topic_id"])Notification("Processing your request...", timeout=None, style="success")
    # Check for generation intent
    if any(keyword in message_lower for keyword in ["create", "generate", "make"]):
      if "lesson" in message_lower:rate_worksheet":_generation(params.get("duration", "45 minutes"))
        # Extract durationeneration(params.get("difficulty", "mixed"))
        duration = "45 minutes"
        if "30" in message_lower:on(params.get("difficulty", "mixed"))on(params["grade"])
          duration = "30 minutes"
        elif "60" in message_lower or "hour" in message_lower:
          duration = "60 minutes"
        return "generate_lesson", {"duration": duration}  self.handle_general_query()    
      
      if "worksheet" in message_lower:arams["topic_id"])to determine intent."""
        # Extract difficultyor
        difficulty = "mixed")
        if "easy" in message_lower:ion", "45 minutes"))
          difficulty = "easy"
        elif "medium" in message_lower:determine intent."""(st|nd|rd|th)?\s*grade', message_lower)
          difficulty = "medium"isonion(params.get("difficulty", "mixed"))
        elif "hard" in message_lower:ower()o determine intent."""tch.group(2))
          difficulty = "hard"
        return "generate_worksheet", {"difficulty": difficulty}# Check for grade levelmessage_lower = message.lower()    self.handle_help_request()
    *(\d+)|(\d+)(st|nd|rd|th)?\s*grade', message_lower)
    # Check for topic research intent
    if "topic" in message_lower and any(word in message_lower for word in ["show", "list", "suggest"]):p(1) or grade_match.group(2))e\s*(\d+)|(\d+)(st|nd|rd|th)?\s*grade', message_lower)):topic|number)\s*(\d+)', message_lower)
      return "research_topics", {}  return "set_grade", {"grade": grade}if grade_match:  topic_num = int(topic_match.group(1)) - 1
    tch.group(2))topic_num}
    # Check for help intent
    if "help" in message_lower or "what can you do" in message_lower:opic|number)\s*(\d+)', message_lower):tent
      return "help", {}  topic_match = re.search(r'(?:topic|number)\s*(\d+)', message_lower)# Check for topic selection intent any(keyword in message_lower for keyword in ["create", "generate", "make"]):
    t(topic_match.group(1)) - 1?:topic|number)\s*(\d+)', message_lower):e(self, message): message_lower:
    # Default intentc_num}r)\s*(\d+)', message_lower)t."""
    return "general_query", {"query": message}      topic_num = int(topic_match.group(1)) - 1  # Convert to lowercase for comparison      duration = "45 minutes"
  eration intentt_topic", {"topic_id": topic_num} message.lower()message_lower:
  # Intent handlersyword in ["create", "generate", "make"]):
  def handle_grade_selection(self, grade)::
    """Handle grade level selection.""" durationd in message_lower for keyword in ["create", "generate", "make"]): re.search(r'grade\s*(\d+)|(\d+)(st|nd|rd|th)?\s*grade', message_lower)n = "60 minutes"
    # Store grade minutes"essage_lower:lesson", {"duration": duration}
    self.grade = grade    if "30" in message_lower:    # Extract duration  grade = int(grade_match.group(1) or grade_match.group(2))  
    0 minutes"minutes"", {"grade": grade} message_lower:
    # Generate response
    response = f"Great! I'll help you create materials for Grade {grade}. Would you like me to suggest some math topics suitable for this grade level?"
    self.add_message("assistant", response)      return "generate_lesson", {"duration": duration}  if re.search(r'(?:topic|number)\s*(\d+)', message_lower):      elif "60" in message_lower or "hour" in message_lower:      if "easy" in message_lower:
  sage_lower)
  def handle_topic_research(self):) - 1tion": duration}
    """Handle topic research request.""": topic_num}
    if not hasattr(self, 'grade'):
      self.add_message("assistant", "Before I can suggest topics, please tell me what grade level you're teaching (1-5).")easy" in message_lower:for generation intenttract difficultyfficulty = "hard"
      return      difficulty = "easy"if any(keyword in message_lower for keyword in ["create", "generate", "make"]):    difficulty = "mixed"    return "generate_worksheet", {"difficulty": difficulty}
    
    # Call server function to research topics  difficulty = "medium"# Extract duration  difficulty = "easy"eck for topic research intent
    try:
      # Use default US Common Core curriculum for simplicity
      research_data = anvil.server.call('get_research_data', self.grade, "US Common Core")  return "generate_worksheet", {"difficulty": difficulty}    duration = "30 minutes"  elif "hard" in message_lower:
      ssage_lower:d"
      # Store research data: difficulty}can you do" in message_lower:
      self.research_data = research_data "topic" in message_lower and any(word in message_lower for word in ["show", "list", "suggest"]):  return "generate_lesson", {"duration": duration}turn "help", {}
      
      # Format topic list for display
      topics = anvil.server.call('get_topics_list', research_data)
      topics_html = "<h3>Math Topics</h3><ol>" "help" in message_lower or "what can you do" in message_lower:  difficulty = "mixed"
      lower:t
      for topic in topics:
        topics_html += f"<li><strong>{topic['title']}</strong>: {topic['description']}</li>"Default intent  elif "medium" in message_lower:return "help", {}"Handle grade level selection."""
      
      topics_html += "</ol><p>Reply with the topic number you'd like to use.</p>"if "hard" in message_lower:Default intentlf.grade = grade
      
      # Set content to display topicsy": difficulty}
      self.set_content("topics", topics_html)"Handle grade level selection."""nt handlerssponse = f"Great! I'll help you create materials for Grade {grade}. Would you like me to suggest some math topics suitable for this grade level?"
      elf, grade):ant", response)
      # Add response to chat
      self.add_message("assistant", f"I've found some math topics for Grade {self.grade}. You can see them in the preview panel. To select a topic, reply with the topic number (e.g., 'I'd like topic 3').")turn "research_topics", {}Store gradehandle_topic_research(self):
      
    except Exception as e:ics suitable for this grade level?"
      self.add_message("assistant", f"I encountered an error while researching topics: {str(e)}. Please try again.")  self.add_message("assistant", response)  if "help" in message_lower or "what can you do" in message_lower:  # Generate response    self.add_message("assistant", "Before I can suggest topics, please tell me what grade level you're teaching (1-5).")
  th topics suitable for this grade level?"
  def handle_topic_selection(self, topic_id)::
    """Handle topic selection."""
    if not hasattr(self, 'research_data'):
      self.add_message("assistant", "Before selecting a topic, please let me help you research topics for your grade level.")dd_message("assistant", "Before I can suggest topics, please tell me what grade level you're teaching (1-5).")search request."""default US Common Core curriculum for simplicity
      return  returnIntent handlersif not hasattr(self, 'grade'):  research_data = anvil.server.call('get_research_data', self.grade, "US Common Core")
    _grade_selection(self, grade):lf.add_message("assistant", "Before I can suggest topics, please tell me what grade level you're teaching (1-5).")
    try:tion to research topicsvel selection."""
      # Get topic data
      topic_data = anvil.server.call('get_learning_outcome', self.research_data, topic_id)# Use default US Common Core curriculum for simplicitylf.grade = gradeCall server function to research topics
      vil.server.call('get_research_data', self.grade, "US Common Core")
      # Store topic datast', research_data)
      self.topic_data = topic_datathis grade level?"mon Core")
      self.topic_context = anvil.server.call('create_topic_context', topic_data)self.research_data = research_datalf.add_message("assistant", response)
      
      # Format topic details for display
      topic_html = f"<h3>{topic_data.get('title', '')}</h3>"
      topic_html += f"<p><strong>Description:</strong> {topic_data.get('description', '')}</p>"
      topic_html += f"<p><strong>Learning Outcome:</strong> {topic_data.get('learning_outcome', '')}</p>"self.add_message("assistant", "Before I can suggest topics, please tell me what grade level you're teaching (1-5).")topics = anvil.server.call('get_topics_list', research_data)
      
      # Add context informationtitle']}</strong>: {topic['description']}</li>"
      context = topic_data.get("context", {})o research topicsn topics:
      if context:umber you'd like to use.</p>"
        topic_html += "<h4>Context Information</h4>"e default US Common Core curriculum for simplicity.add_message("assistant", f"I've found some math topics for Grade {self.grade}. You can see them in the preview panel. To select a topic, reply with the topic number (e.g., 'I'd like topic 3').")
         display topicsanvil.server.call('get_research_data', self.grade, "US Common Core")</ol><p>Reply with the topic number you'd like to use.</p>"
        # Key conceptscs_html)
        if "key_concepts" in context:
          topic_html += "<p><strong>Key Concepts:</strong></p><ul>"
          for concept in context["key_concepts"]:d some math topics for Grade {self.grade}. You can see them in the preview panel. To select a topic, reply with the topic number (e.g., 'I'd like topic 3').")
            topic_html += f"<li>{concept}</li>"
          topic_html += "</ul>"pt Exception as e:pics = anvil.server.call('get_topics_list', research_data)lf.add_message("assistant", f"I've found some math topics for Grade {self.grade}. You can see them in the preview panel. To select a topic, reply with the topic number (e.g., 'I'd like topic 3').")ot hasattr(self, 'research_data'):
        assistant", f"I encountered an error while researching topics: {str(e)}. Please try again.")>Math Topics</h3><ol>"e selecting a topic, please let me help you research topics for your grade level.")
        # Misconceptions
        if "misconceptions" in context:
          topic_html += "<p><strong>Common Misconceptions:</strong></p><ul>" {topic['description']}</li>"
          for misc in context["misconceptions"]:
            topic_html += f"<li>{misc}</li>"nt", "Before selecting a topic, please let me help you research topics for your grade level.")eply with the topic number you'd like to use.</p>""".call('get_learning_outcome', self.research_data, topic_id)
          topic_html += "</ul>"turn hasattr(self, 'research_data'):
        opicssage("assistant", "Before selecting a topic, please let me help you research topics for your grade level.")c data
        # Examples
        if "examples" in context:
          topic_html += "<p><strong>Examples:</strong></p><ul>"rning_outcome', self.research_data, topic_id)
          for example in context["examples"]:. You can see them in the preview panel. To select a topic, reply with the topic number (e.g., 'I'd like topic 3').")
            topic_html += f"<li>{example}</li>"lf.research_data, topic_id)_data.get('title', '')}</h3>"
          topic_html += "</ul>"self.topic_data = topic_datacept Exception as e:topic_html += f"<p><strong>Description:</strong> {topic_data.get('description', '')}</p>"
      ('create_topic_context', topic_data)untered an error while researching topics: {str(e)}. Please try again.")ic_data.get('learning_outcome', '')}</p>"
      # Set content to display topic details
      self.set_content("topic_details", topic_html)# Format topic details for displayhandle_topic_selection(self, topic_id):self.topic_context = anvil.server.call('create_topic_context', topic_data)# Add context information
      pic_data.get('title', '')}</h3>"n."""
      # Add response to chat
      self.add_message("assistant", f"Great choice! You've selected **{topic_data.get('title', '')}**. Would you like me to create a lesson plan for this topic? Just let me know if you want a 30, 45, or 60-minute lesson.")  topic_html += f"<p><strong>Learning Outcome:</strong> {topic_data.get('learning_outcome', '')}</p>"  self.add_message("assistant", "Before selecting a topic, please let me help you research topics for your grade level.")  topic_html = f"<h3>{topic_data.get('title', '')}</h3>"    topic_html += "<h4>Context Information</h4>"
    c_data.get('description', '')}</p>"
    except Exception as e:
      self.add_message("assistant", f"I had trouble selecting that topic: {str(e)}. Please try again.")    context = topic_data.get("context", {})  try:          if "key_concepts" in context:
  
  def handle_lesson_generation(self, duration):mation</h4>"t_learning_outcome', self.research_data, topic_id), {})ncepts"]:
    """Handle lesson plan generation."""
    if not hasattr(self, 'topic_data') or not hasattr(self, 'topic_context'):
      self.add_message("assistant", "Before I can create a lesson plan, please select a topic first.")key_concepts" in context:opic_data = topic_data
      return      topic_html += "<p><strong>Key Concepts:</strong></p><ul>"  self.topic_context = anvil.server.call('create_topic_context', topic_data)    # Key concepts    # Misconceptions
      for concept in context["key_concepts"]: "key_concepts" in context:if "misconceptions" in context:
    try: += f"<li>{concept}</li>"etails for display= "<p><strong>Key Concepts:</strong></p><ul>"= "<p><strong>Common Misconceptions:</strong></p><ul>"
      # Get parameters', '')}</h3>"oncepts"]:ptions"]:
      grade = getattr(self, 'grade', 3), '')}</p>""
      curriculum = "US Common Core"  # Defaulttcome:</strong> {topic_data.get('learning_outcome', '')}</p>"
      topic_data = self.topic_data
      topic_context = self.topic_contextong></p><ul>"
      learning_outcome = topic_data.get("learning_outcome", "")    for misc in context["misconceptions"]:context = topic_data.get("context", {})  if "misconceptions" in context:  if "examples" in context:
      <li>{misc}</li>"mon Misconceptions:</strong></p><ul>"<strong>Examples:</strong></p><ul>"
      # Generate lesson plan
      loading_message = f"Generating a {duration} lesson plan on {topic_data.get('title', '')}..."
      self.add_message("assistant", loading_message)  # Examples  # Key concepts    topic_html += "</ul>"    topic_html += "</ul>"
      
      lesson_plan = anvil.server.call(rong>Examples:</strong></p><ul>"rong>Key Concepts:</strong></p><ul>"
        'generate_lesson_plan',context["examples"]:context["key_concepts"]:context:opic_details", topic_html)
        learning_outcome,pic_html += f"<li>{example}</li>"pic_html += f"<li>{concept}</li>"c_html += "<p><strong>Examples:</strong></p><ul>"
        grade,l += "</ul>"l += "</ul>"le in context["examples"]:e to chat
        curriculum,ple}</li>"ssage("assistant", f"Great choice! You've selected **{topic_data.get('title', '')}**. Would you like me to create a lesson plan for this topic? Just let me know if you want a 30, 45, or 60-minute lesson.")
        duration,o display topic detailsons+= "</ul>"
        topic_contextelf.set_content("topic_details", topic_html) if "misconceptions" in context:pt Exception as e:
      )    topic_html += "<p><strong>Common Misconceptions:</strong></p><ul>"# Set content to display topic detailsself.add_message("assistant", f"I had trouble selecting that topic: {str(e)}. Please try again.")
      hattext["misconceptions"]:opic_details", topic_html)
      # Store lesson planf"Great choice! You've selected **{topic_data.get('title', '')}**. Would you like me to create a lesson plan for this topic? Just let me know if you want a 30, 45, or 60-minute lesson.")c}</li>"
      self.lesson_plan = lesson_plan  topic_html += "</ul>"# Add response to chat"Handle lesson plan generation."""
      ', '')}**. Would you like me to create a lesson plan for this topic? Just let me know if you want a 30, 45, or 60-minute lesson.")not hasattr(self, 'topic_context'):
      # Set content to display lesson plane selecting that topic: {str(e)}. Please try again.")
      self.set_content("lesson_plan", lesson_plan) "examples" in context:cept Exception as e:return
      on(self, duration):<strong>Examples:</strong></p><ul>"stant", f"I had trouble selecting that topic: {str(e)}. Please try again.")
      # Add response to chat
      self.add_message("assistant", f"I've created a {duration} lesson plan on {topic_data.get('title', '')} for Grade {grade}. You can see it in the preview panel and download it as a PDF. Would you like me to create a worksheet to go with this lesson?")if not hasattr(self, 'topic_data') or not hasattr(self, 'topic_context'):        topic_html += f"<li>{example}</li>"f handle_lesson_generation(self, duration):  # Get parameters
    sistant", "Before I can create a lesson plan, please select a topic first.")/ul>"generation.""", 'grade', 3)
    except Exception as e:
      self.add_message("assistant", f"I encountered an error generating the lesson plan: {str(e)}. Please try again.")      # Set content to display topic details    self.add_message("assistant", "Before I can create a lesson plan, please select a topic first.")    topic_data = self.topic_data
  
  def handle_worksheet_generation(self, difficulty):
    """Handle worksheet generation."""
    if not hasattr(self, 'lesson_plan'):
      self.add_message("assistant", "I need to create a lesson plan first before I can make a worksheet. Would you like me to create a lesson plan?")data = self.topic_datar(self, 'grade', 3)g_message = f"Generating a {duration} lesson plan on {topic_data.get('title', '')}..."
      return  topic_context = self.topic_contextexcept Exception as e:  curriculum = "US Common Core"  # Default  self.add_message("assistant", loading_message)
    arning_outcome = topic_data.get("learning_outcome", "")lf.add_message("assistant", f"I had trouble selecting that topic: {str(e)}. Please try again.")pic_data = self.topic_data
    try:
      # Get parametersation):a.get("learning_outcome", "")
      topic_data = self.topic_dataduration} lesson plan on {topic_data.get('title', '')}..."
      topic_context = self.topic_contextloading_message)') or not hasattr(self, 'topic_context'):
      lesson_plan = self.lesson_plan'title', '')}..."
      learning_outcome = topic_data.get("learning_outcome", "")lesson_plan = anvil.server.call(returnself.add_message("assistant", loading_message)  duration,
      lan',
      # Generate worksheet
      loading_message = f"Generating a {difficulty} difficulty worksheet..."
      self.add_message("assistant", loading_message)  curriculum,grade = getattr(self, 'grade', 3)  learning_outcome,# Store lesson plan
      
      worksheet = anvil.server.call(
        'generate_worksheet',f.topic_context
        learning_outcome, = topic_data.get("learning_outcome", "")esson_plan)
        topic_context,
        lesson_plan,esson planplan = lesson_plan
        difficultyoading_message = f"Generating a {duration} lesson plan on {topic_data.get('title', '')}..."Store lesson planelf.add_message("assistant", f"I've created a {duration} lesson plan on {topic_data.get('title', '')} for Grade {grade}. You can see it in the preview panel and download it as a PDF. Would you like me to create a worksheet to go with this lesson?")
      )self.add_message("assistant", loading_message)# Set content to display lesson planself.lesson_plan = lesson_plan
      sson_plan)
      # Store worksheet.call(red an error generating the lesson plan: {str(e)}. Please try again.")
      self.worksheet = worksheet  'generate_lesson_plan',# Add response to chatself.set_content("lesson_plan", lesson_plan)
      uration} lesson plan on {topic_data.get('title', '')} for Grade {grade}. You can see it in the preview panel and download it as a PDF. Would you like me to create a worksheet to go with this lesson?")
      # Set content to display worksheet
      self.set_content("worksheet", worksheet)  curriculum,cept Exception as e:self.add_message("assistant", f"I've created a {duration} lesson plan on {topic_data.get('title', '')} for Grade {grade}. You can see it in the preview panel and download it as a PDF. Would you like me to create a worksheet to go with this lesson?") not hasattr(self, 'lesson_plan'):
       encountered an error generating the lesson plan: {str(e)}. Please try again.")e a lesson plan first before I can make a worksheet. Would you like me to create a lesson plan?")
      # Add response to chat
      )  self.add_message("assistant", f"I've created a {difficulty} difficulty worksheet to accompany your lesson plan. You can see it in the preview panel and download it as a PDF. Is there anything you'd like me to change or improve?")f handle_worksheet_generation(self, difficulty):  self.add_message("assistant", f"I encountered an error generating the lesson plan: {str(e)}. Please try again.")
      
      # Store lesson plan
      self.lesson_plan = lesson_plan    self.add_message("assistant", f"I encountered an error generating the worksheet: {str(e)}. Please try again.")    self.add_message("assistant", "I need to create a lesson plan first before I can make a worksheet. Would you like me to create a lesson plan?")  """Handle worksheet generation."""    topic_data = self.topic_data
      
      # Set content to display lesson plan):lesson plan first before I can make a worksheet. Would you like me to create a lesson plan?")n_plan
      self.set_content("lesson_plan", lesson_plan)uest."""ing_outcome", "")
      
      # Add response to chat<h3>Teacher Copilot Help</h3>  topic_data = self.topic_datatry:  # Generate worksheet
      self.add_message("assistant", f"I've created a {duration} lesson plan on {topic_data.get('title', '')} for Grade {grade}. You can see it in the preview panel and download it as a PDF. Would you like me to create a worksheet to go with this lesson?")
    <p>I can help you create math lesson plans and worksheets. Here's how to use me:</p>  lesson_plan = self.lesson_plan  topic_data = self.topic_data  self.add_message("assistant", loading_message)
    except Exception as e:ng_outcome = topic_data.get("learning_outcome", "")pic_context = self.topic_context
      self.add_message("assistant", f"I encountered an error generating the lesson plan: {str(e)}. Please try again.")
  )</li>
  def handle_worksheet_generation(self, difficulty):
    """Handle worksheet generation."""n</li>
    if not hasattr(self, 'lesson_plan'):/li>
      self.add_message("assistant", "I need to create a lesson plan first before I can make a worksheet. Would you like me to create a lesson plan?")><strong>Download content</strong> - Export lesson plans and worksheets as PDFs</li>ksheet = anvil.server.call(f.add_message("assistant", loading_message)ifficulty
      return</ol>    'generate_worksheet',    )
    
    try:strong>Example commands:</strong></p>topic_context,'generate_worksheet',Store worksheet
      # Get parameters
      topic_data = self.topic_data
      topic_context = self.topic_contextli>
      lesson_plan = self.lesson_plan
      learning_outcome = topic_data.get("learning_outcome", "")/li>
      >"Generate an easy worksheet"</li>f.worksheet = worksheetresponse to chat
      # Generate worksheetl>Store worksheetelf.add_message("assistant", f"I've created a {difficulty} difficulty worksheet to accompany your lesson plan. You can see it in the preview panel and download it as a PDF. Is there anything you'd like me to change or improve?")
      loading_message = f"Generating a {difficulty} difficulty worksheet...""""  # Set content to display worksheet  self.worksheet = worksheet
      self.add_message("assistant", loading_message)
      tr(e)}. Please try again.")
      worksheet = anvil.server.call(self.set_content("help", help_message)  # Add response to chat  self.set_content("worksheet", worksheet)
        'generate_worksheet',ed a {difficulty} difficulty worksheet to accompany your lesson plan. You can see it in the preview panel and download it as a PDF. Is there anything you'd like me to change or improve?")
        learning_outcome,
        topic_context,  self.add_message("assistant", "I can help you create math lesson plans and worksheets. You can see instructions on how to use me in the preview panel. What would you like to do?")  except Exception as e:    self.add_message("assistant", f"I've created a {difficulty} difficulty worksheet to accompany your lesson plan. You can see it in the preview panel and download it as a PDF. Is there anything you'd like me to change or improve?")  help_message = """
        lesson_plan,erating the worksheet: {str(e)}. Please try again.")
        difficulty
      )
      ng assistant. I can help you create lesson plans and worksheets for elementary math classes. To get started, please tell me what grade level you're teaching (1-5)."
      # Store worksheet  self.add_message("assistant", response)  help_message = """def handle_help_request(self):  <ol>
      self.worksheet = worksheet
      gs):
      # Set content to display worksheetandle download button click.""" can help you create math lesson plans and worksheets. Here's how to use me:</p>Teacher Copilot Help</h3>i><strong>Generate a lesson plan</strong> - Ask me to create a 30, 45, or 60-minute lesson</li>
      self.set_content("worksheet", worksheet)
      son_plan" and hasattr(self, 'lesson_plan'):s. Here's how to use me:</p></strong> - Export lesson plans and worksheets as PDFs</li>
      # Add response to chat/strong> - Tell me which grade you're teaching (1-5)</li>
      self.add_message("assistant", f"I've created a {difficulty} difficulty worksheet to accompany your lesson plan. You can see it in the preview panel and download it as a PDF. Is there anything you'd like me to change or improve?")
    "worksheet" and hasattr(self, 'worksheet'):son plan</strong> - Ask me to create a 30, 45, or 60-minute lesson</li>level</strong> - Tell me which grade you're teaching (1-5)</li></strong></p>
    except Exception as e:et</strong> - Request a worksheet to go with your lesson</li>strong> - I'll suggest topics for that grade level</li>
      self.add_message("assistant", f"I encountered an error generating the worksheet: {str(e)}. Please try again.")ename = "worksheet.pdf"strong>Download content</strong> - Export lesson plans and worksheets as PDFs</li>strong>Generate a lesson plan</strong> - Ask me to create a 30, 45, or 60-minute lesson</li>I'm teaching grade 3"</li>
  
  def handle_help_request(self):alert("No content available to download")ad content</strong> - Export lesson plans and worksheets as PDFs</li> like to use topic 2"</li>
    """Handle help request."""  return><strong>Example commands:</strong></p>ol><li>"Create a 45-minute lesson plan"</li>
    help_message = """
    <h3>Teacher Copilot Help</h3>
    pdf_media = anvil.server.call('generate_pdf', content, filename)<li>"Show me topics for grade 4"</li>l>"
    <p>I can help you create math lesson plans and worksheets. Here's how to use me:</p>ade 3"</li>
    li>
    <ol>anvil.media.download(pdf_media)<li>"Generate an easy worksheet"</li><li>"I'd like to use topic 2"</li>lf.set_content("help", help_message)
      <li><strong>Specify grade level</strong> - Tell me which grade you're teaching (1-5)</li>
      <li><strong>Choose a topic</strong> - I'll suggest topics for that grade level</li>
      <li><strong>Generate a lesson plan</strong> - Ask me to create a 30, 45, or 60-minute lesson</li>      anvil.alert(f"Error downloading content: {str(e)}")        </ul>    self.add_message("assistant", "I can help you create math lesson plans and worksheets. You can see instructions on how to use me in the preview panel. What would you like to do?")
      <li><strong>Generate a worksheet</strong> - Request a worksheet to go with your lesson</li>
      <li><strong>Download content</strong> - Export lesson plans and worksheets as PDFs</li>shelp", help_message)
    </ol>
     To get started, please tell me what grade level you're teaching (1-5)."
    <p><strong>Example commands:</strong></p>oller."""eate math lesson plans and worksheets. You can see instructions on how to use me in the preview panel. What would you like to do?")
    <ul>from content_generator import LessonPlanController  # Add response to chat  from content_generator import LessonPlanControllerglobal _controller
      <li>"I'm teaching grade 3"</li>ant", "I can help you create math lesson plans and worksheets. You can see instructions on how to use me in the preview panel. What would you like to do?")(self, **event_args):
      <li>"Show me topics for grade 4"</li>"""
      <li>"I'd like to use topic 2"</li>controller = LessonPlanController()  response = "I'm your math lesson planning assistant. I can help you create lesson plans and worksheets for elementary math classes. To get started, please tell me what grade level you're teaching (1-5)."def handle_general_query(self):  if not self.file_loader.file:  controller = LessonPlanController()  import os
      <li>"Create a 45-minute lesson plan"</li>se) query when intent is not clear."""ease select a file to upload.")
      <li>"Generate an easy worksheet"</li>arted, please tell me what grade level you're teaching (1-5)."
    </ul>  return controller.get_research_data(grade, curriculum)  def download_content(self, **event_args):    self.add_message("assistant", response)        return controller.get_research_data(grade, curriculum)    api_key = anvil.server.get_app_origin_info().get("api_key") or os.getenv("OPENAI_API_KEY")
    """
    
    # Set content to display help
    self.set_content("help", help_message)h data."""
    from content_generator import LessonPlanController      filename = "lesson_plan.pdf"    if self.content_type == "lesson_plan" and hasattr(self, 'lesson_plan'):      file_data = self.file_loader.fileil.server.call('import_document', file_data)eey):
    # Add response to chatet" and hasattr(self, 'worksheet'):f.lesson_planl.server.call('import_document', file_data)eey):
    self.add_message("assistant", "I can help you create math lesson plans and worksheets. You can see instructions on how to use me in the preview panel. What would you like to do?")
  controller = LessonPlanController()      filename = "worksheet.pdf"    elif self.content_type == "worksheet" and hasattr(self, 'worksheet'):      if not doc_id.startswith("Error"):"""Server function to get topics list from research data."""global _controller
  def handle_general_query(self):llyrver state
    """Handle general query when intent is not clear."""
    response = "I'm your math lesson planning assistant. I can help you create lesson plans and worksheets for elementary math classes. To get started, please tell me what grade level you're teaching (1-5)."  return controller.get_topics_list(research_data)        return      else:            self.documents = []      
    self.add_message("assistant", response)
  
  def download_content(self, **event_args):
    """Handle download button click."""opic."""
    try:from content_generator import LessonPlanController    # Trigger download    pdf_media = anvil.server.call('generate_pdf', content, filename)        anvil.Notification(f"Document '{file_data.name}' uploaded successfully.",   return controller.get_topics_list(research_data)return True
      if self.content_type == "lesson_plan" and hasattr(self, 'lesson_plan'):style="success").show()
        content = self.lesson_plan
        filename = "lesson_plan.pdf"controller = LessonPlanController()  except Exception as e:    anvil.media.download(pdf_media)      else:  print(f"Error getting topics list: {str(e)}")f get_research_data(grade, curriculum):
      elif self.content_type == "worksheet" and hasattr(self, 'worksheet'): {str(e)}")ocument: {doc_id}")(e)}"get research data from controller."""
        content = self.worksheet
        filename = "worksheet.pdf"  return controller.get_learning_outcome(research_data, topic_id)# Server-side functions      anvil.alert(f"Error downloading content: {str(e)}")    except Exception as e:@anvil.server.callable  
      else:h_data, topic_id):
        anvil.alert("No content available to download")
        return""
      
      # Call server function to generate PDFfrom content_generator import LessonPlanController"""Server function to get research data from controller."""  try:  f get_topics_list(research_data):
      pdf_media = anvil.server.call('generate_pdf', content, filename)anController_type == "lesson_plan" and hasattr(self, 'lesson_plan'):erto get topics list from research data."""
      
      # Trigger downloadcontroller = LessonPlanController()# Create controller      filename = "lesson_plan.pdf"  
      anvil.media.download(pdf_media)ksheet" and hasattr(self, 'worksheet'):me
      
    except Exception as e:  return controller.create_topic_context(topic_data)  # Get research data        filename = "worksheet.pdf"  
      anvil.alert(f"Error downloading content: {str(e)}") curriculum)
  
  def toggle_settings(self, **event_args):curriculum, duration, topic_context):rch data."""
    """Toggle settings panel visibility."""
    self.settings_panel.visible = not self.settings_panel.visiblefrom content_generator import LessonPlanController"""Server function to get topics list from research data."""    # Call server function to generate PDFnvil.server.callable
anControlleril.server.call('generate_pdf', content, filename)ext(topic_data):ome
  def save_api_key(self, **event_args):
    """Save API key."""controller = LessonPlanController()# Create controller    # Trigger downloadtry:
    api_key = self.api_key_input.text.strip()r import LessonPlanController
    if not api_key:
      anvil.alert("Please enter an API key.")  return controller.generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context)  # Get topics list    except Exception as e:    # Create controller  """Server function to create topic context."""
      return_data)ror downloading content: {str(e)}")nPlanController()troller_instance()
    
    try:ontext, lesson_plan, difficulty): a topic."""
      # Save API key on server
      result = anvil.server.call('set_api_key', api_key)from content_generator import LessonPlanController"""Server function to get learning outcome for a topic."""f get_research_data(grade, curriculum):
      if result:anControllerto get research data from controller.""" e:e
        anvil.Notification("API key saved successfully.", timeout=3, style="success").show()um, duration, topic_context):
      else:controller = LessonPlanController()# Create controller  return f"Error: {str(e)}""""Server function to generate a lesson plan."""
        anvil.alert("Failed to save API key.")
    except Exception as e:
      anvil.alert(f"Error saving API key: {str(e)}")  return controller.generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty)  # Get learning outcome  def generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context):  # Generate lesson plan
earch_data, topic_id) generate a lesson plan."""nerate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context)
# Server-side functions
@anvil.server.callable
def get_research_data(grade, curriculum): and return as Media object."""nerator import LessonPlanControllercontext(topic_data):lableg_outcome, topic_context, lesson_plan, difficulty):
  """Server function to get research data from controller."""
  from content_generator import LessonPlanControllerfrom content_generator import LessonPlanController# Create controllerfrom content_generator import LessonPlanController"""Server function to get topics list from research data."""  controller = LessonPlanController()controller = get_controller_instance()
  ller()anController
  # Create controller
  controller = LessonPlanController()try:# Create topic contextcontroller = LessonPlanController()# Create controller  if not controller.validate_api_key():return controller.generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty)
  ancee_topic_context(topic_data)issing or invalid. Please add your OpenAI API key in the settings.")
  # Get research data
  return controller.get_research_data(grade, curriculum)opic_context(topic_data)tson planontent, filename):

@anvil.server.callablewith tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:"Server function to generate a lesson plan."""il.server.callableempfile
def get_topics_list(research_data):erutcome, grade, curriculum, duration, topic_context):
  """Server function to get topics list from research data."""te_pdf(content, tmp_file.name) structured error
  from content_generator import LessonPlanControllerrt learning outcome for a topic."""ng lesson plan: {str(e)}")
    # Read PDF into bytesntroller = LessonPlanController() content_generator import LessonPlanControllerreturn f"Error: {str(e)}"th tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
  # Create controller 'rb') as f:
  controller = LessonPlanController()
    turn controller.generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context)roller = LessonPlanController()generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty):
  # Get topics listemp file"" convert to Media
  return controller.get_topics_list(research_data).exists(tmp_file.name):llableler.generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context) outcomeb') as f:
        os.unlink(tmp_file.name)def generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty):  return controller.get_learning_outcome(research_data, topic_id)    from content_generator import LessonPlanController      pdf_bytes = f.read()
@anvil.server.callable
def get_learning_outcome(research_data, topic_id):_plan, difficulty):
  """Server function to get learning outcome for a topic."""      return anvil.BlobMedia('application/pdf', pdf_bytes, name=filename)    """Server function to generate a worksheet."""def create_topic_context(topic_data):    controller = LessonPlanController()    media = anvil.BlobMedia('application/pdf', pdf_bytes, name=filename)














































































# https://anvil.works/build#clone:YOURANVILAPPLINK# Create a clone of this example in your own app by visiting:    return False  except Exception as e:    return True    app_tables.api_keys.add_row(key=api_key)    # Save API key securely  try:  """Save API key on the server."""def set_api_key(api_key):@anvil.server.callable    return media    # Return Media        media = anvil.BlobMedia('application/pdf', pdf_bytes, name=filename)    # Create Media object          pdf_bytes = f.read()    with open(pdf_path, 'rb') as f:    # Read PDF and convert to Media        pdf_path = controller._generate_pdf(content, tmp_file.name)    # Generate PDF  with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:  # Create temporary file    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController  import tempfile  """Generate PDF and return as Media object."""def generate_pdf(content, filename):@anvil.server.callable  return controller.generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty)  # Generate worksheet    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController  """Server function to generate a worksheet."""def generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty):@anvil.server.callable  return controller.generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context)  # Generate lesson plan    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController  """Server function to generate a lesson plan."""def generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context):@anvil.server.callable  return controller.create_topic_context(topic_data)  # Create topic context    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController







# https://anvil.works/build#clone:YOURANVILAPPLINK# Create a clone of this example in your own app by visiting:    raise Exception(f"Could not generate PDF: {str(e)}")    print(f"Error generating PDF: {str(e)}")  except Exception as e:  
































# https://anvil.works/build#clone:YOURANVILAPPLINK# Create a clone of this example in your own app by visiting:    return media    # Return Media        media = anvil.BlobMedia('application/pdf', pdf_bytes, name=filename)    # Create Media object          pdf_bytes = f.read()    with open(pdf_path, 'rb') as f:    # Read PDF and convert to Media        pdf_path = controller._generate_pdf(content, tmp_file.name)    # Generate PDF  with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:  # Create temporary file    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController  import tempfile  """Generate PDF and return as Media object."""def generate_pdf(content, filename):@anvil.server.callable  return controller.generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty)  # Generate worksheet    controller = LessonPlanController()  # Create controller


































# https://anvil.works/build#clone:YOURANVILAPPLINK# Create a clone of this example in your own app by visiting:    return media    # Return Media        media = anvil.BlobMedia('application/pdf', pdf_bytes, name=filename)    # Create Media object          pdf_bytes = f.read()    with open(pdf_path, 'rb') as f:    # Read PDF and convert to Media        pdf_path = controller._generate_pdf(content, tmp_file.name)    # Generate PDF  with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:  # Create temporary file    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController  import tempfile  """Generate PDF and return as Media object."""def generate_pdf(content, filename):@anvil.server.callable  return controller.generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty)  # Generate worksheet    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController







































# https://anvil.works/build#clone:YOURANVILAPPLINK# Create a clone of this example in your own app by visiting:    return f"Error: {str(e)}"    print(f"Error generating PDF: {str(e)}")  except Exception as e:          return media      # Return Media            media = anvil.BlobMedia('application/pdf', pdf_bytes, name=filename)      # Create Media object              pdf_bytes = f.read()      with open(pdf_path, 'rb') as f:      # Read PDF and convert to Media            pdf_path = controller._generate_pdf(content, tmp_file.name)      # Generate PDF    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:    # Create temporary file        controller = LessonPlanController()    # Create controller        from content_generator import LessonPlanController    import tempfile  try:  """Generate PDF and return as Media object."""def generate_pdf(content, filename):@anvil.server.callable    return f"Error: {str(e)}"    print(f"Error generating worksheet: {str(e)}")




























































# https://anvil.works/build#clone:YOURANVILAPPLINK# Create a clone of this example in your own app by visiting:






    return f"Error: {str(e)}"  except Exception as e:    return doc_id



        os.unlink(file_path)    # Clean up temp file        doc_id = controller.document_manager.import_document(file_path)



    controller = get_controller_instance()    # Import to document manager          file_path = tmp_file.name      tmp_file.write(file_data.get_bytes())    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_data.name)[1]) as tmp_file:    # Save to temp file  try:    import os  import tempfile  """Import document from file data."""def import_document(file_data):@anvil.server.callable    return media    # Return Media        media = anvil.BlobMedia('application/pdf', pdf_bytes, name=filename)    # Create Media object          pdf_bytes = f.read()    with open(pdf_path, 'rb') as f:    # Read PDF and convert to Media        pdf_path = controller._generate_pdf(content, tmp_file.name)    # Generate PDF  with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:  # Create temporary file    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController  import tempfile  """Generate PDF and return as Media object."""def generate_pdf(content, filename):@anvil.server.callable  return controller.generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty)  # Generate worksheet    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController  """Server function to generate a worksheet."""def generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty):@anvil.server.callable  return controller.generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context)  # Generate lesson plan    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController  """Server function to generate a lesson plan."""def generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context):@anvil.server.callable  return controller.create_topic_context(topic_data)  # Create topic context    controller = LessonPlanController()  # Create controller    from content_generator import LessonPlanController




  except Exception as e:      return controller.generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty)    # Generate worksheet        
    # Return Media
    return media

# Create a clone of this example in your own app by visiting:
# https://anvil.works/build#clone:YOURANVILAPPLINK
