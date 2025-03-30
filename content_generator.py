import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tkinter as tk
from tkinter import filedialog

# Load environment variables from .env file (e.g., API keys)
load_dotenv()

#########################
# CONFIG MODULE
#########################

class ConfigManager:
    """Handles application configuration, API keys and model selection."""
    def __init__(self, api_key=None):
        """
        Initialize configuration manager with optional API key.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, tries to get from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def set_api_key(self, api_key):
        """
        Set or update the API key.
        
        Args:
            api_key (str): The OpenAI API key.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not api_key:
            return False
        
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        return True

    def check_api_key(self):
        """
        Check if API key is configured.
        
        Returns:
            bool: True if API key is available, False otherwise
        """
        return self.client is not None

    def save_api_key_to_env(self, api_key):
        """
        Save API key to .env file.
        
        Args:
            api_key (str): The OpenAI API key to save
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            env_path = os.path.join(os.getcwd(), '.env')
            
            # Check if .env file exists
            if not os.path.exists(env_path):
                with open(env_path, 'w') as f:
                    f.write("# API Keys for Lesson Plan Generator\n")
            
            # Load existing variables
            with open(env_path, 'r') as f:
                env_contents = f.read()
            
            # Update or add the API key
            if "OPENAI_API_KEY" in env_contents:
                env_contents = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={api_key}', env_contents)
            else:
                env_contents += f"\nOPENAI_API_KEY={api_key}"
            
            # Save updated .env file
            with open(env_path, 'w') as f:
                f.write(env_contents)
            
            # Update the current client
            self.set_api_key(api_key)
            return True
        except Exception:
            return False

#########################
# RESEARCH MODULE
#########################

class ResearchModule:
    """Responsible for topic research and selection."""
    def __init__(self, config_manager):
        """Initialize with configuration."""
        self.config = config_manager

    def conduct_research(self, grade, curriculum, model="gpt-3.5-turbo-16k"):
        """
        Conduct comprehensive topic research for a specific grade and curriculum.
        
        Args:
            grade (int): Grade level
            curriculum (str): Curriculum standard name
            model (str): OpenAI model to use
        
        Returns:
            dict: Dictionary containing structured research data
        """
        print(f"\nConducting mathematics research for Grade {grade} ({curriculum})...")
        
        research_prompt = f"""
        As an expert mathematics teacher, I need a comprehensive research package for teaching Grade {grade} mathematics according to {curriculum} standards.
        Please provide the following in a clearly structured format:
        
        PART 1: TOPIC SUGGESTIONS
        Provide 10 mathematics topics appropriate for Grade {grade} students according to {curriculum} standards.
        For each topic, include a brief 1-2 sentence description.
        
        PART 2: LEARNING OUTCOMES
        For each of the 10 topics, provide one specific, teachable learning outcome that could be covered in a single lesson.
        
        PART 3: CONTEXTUAL INFORMATION
        For each topic, provide the following contextual information:
        1. Key mathematical concepts and vocabulary students need to learn (5-7 key concepts)
        2. Common misconceptions students have about this topic (3-4 misconceptions)
        3. Prerequisite knowledge students should have (3-4 prerequisites)
        4. Three concrete examples or representations useful for teaching this topic
        
        IMPORTANT: Format your entire response as JSON for easy parsing. Use the following structure exactly:
        {{
            "topics": [
                {{
                    "title": "Topic 1",
                    "description": "Brief description",
                    "learning_outcome": "Specific learning outcome",
                    "context": {{
                        "key_concepts": ["concept 1", "concept 2", ...],
                        "misconceptions": ["misconception 1", "misconception 2", ...],
                        "prerequisites": ["prerequisite 1", "prerequisite 2", ...],
                        "examples": ["example 1", "example 2", "example 3"]
                    }}
                }},
                ... more topics ...
            ]
        }}
        
        Ensure your entire response can be directly parsed as a JSON object.
        """
        
        try:
            print("Generating comprehensive research using OpenAI...")
            response = self.config.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert mathematics curriculum specialist for elementary education."},
                    {"role": "user", "content": research_prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                research_data = json.loads(json_content)
            else:
                research_data = json.loads(content)
            
            print(f"Successfully generated research on {len(research_data['topics'])} topics.")
            return research_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from API response: {str(e)}")
            print("API returned non-JSON content. Falling back to default topics.")
            return self._get_fallback_topics()
        except Exception as e:
            print(f"Error conducting comprehensive research: {str(e)}")
            return self._get_fallback_topics()
    
    def _get_fallback_topics(self):
        """
        Return fallback topics if research fails.
        
        Returns:
            dict: Default research data structure with basic topics
        """
        return {"topics": [
            {"title": "Addition", "description": "Basic addition operations", 
             "learning_outcome": "Add two-digit numbers", 
             "context": {"key_concepts": ["Place value", "Regrouping"], 
                        "misconceptions": ["Forgetting to regroup"], 
                        "prerequisites": ["Number recognition"], 
                        "examples": ["23 + 45 = 68"]}},
            {"title": "Subtraction", "description": "Basic subtraction operations", 
             "learning_outcome": "Subtract two-digit numbers", 
             "context": {"key_concepts": ["Place value", "Borrowing"], 
                        "misconceptions": ["Subtracting the smaller from the larger digit"], 
                        "prerequisites": ["Number recognition"], 
                        "examples": ["45 - 23 = 22"]}}
        ]}

#########################
# WORKSHEET GENERATION MODULE
#########################

class WorksheetGenerator:
    """
    Responsible for generating educational worksheets aligned with lesson plans.
    
    This class creates differentiated practice materials that reinforce 
    the learning outcomes and teaching approaches from the lesson plan.
    It supports various difficulty levels to accommodate diverse student needs.
    """
    
    def __init__(self, config_manager):
        """
        Initialize with configuration.
        
        Args:
            config_manager: ConfigManager instance for API access
        """
        self.config = config_manager
    
    def generate_worksheet(self, learning_outcome, context, lesson_plan=None, difficulty="mixed", model="gpt-3.5-turbo"):
        """
        Generate a worksheet based on learning outcomes and lesson context.
        Creates a worksheet with practice problems that align with the specified
        learning outcome and lesson plan. Difficulty can be adjusted to create
        differentiated practice materials.
        
        Args:
            learning_outcome (str): The specific learning outcome
            context (str): Contextual information about the topic
            lesson_plan (str, optional): The full lesson plan to align with
            difficulty (str): Difficulty level - "easy", "medium", "hard", or "mixed"
            model (str): OpenAI model to use
            
        Returns:
            str: Generated worksheet content
        """
        # Base prompt with learning outcome and context
        base_prompt = f"""
        Create a mathematics worksheet for the following learning outcome:
        {learning_outcome}
        
        Use the following contextual information to enrich the worksheet:
        {context}
        """
        
        # Add lesson plan alignment if available to ensure consistency
        if lesson_plan:
            base_prompt += f"""
            This worksheet MUST align with the following lesson plan. Pay particular attention to:
            1. The instructional approach (I Do, We Do, You Do)
            2. The specific examples used in the lesson
            3. The vocabulary and notation used in the lesson
            
            LESSON PLAN:
            {lesson_plan[:1500]}  # Truncate if too long to fit within token limits
            """
        
        # Add difficulty-specific instructions based on selected level
        difficulty_instructions = {
            "easy": "Create EASY problems that focus on basic understanding and confidence building. Use straightforward examples with minimal steps.",
            "medium": "Create MEDIUM difficulty problems that build on the basics but require some application of concepts.",
            "hard": "Create CHALLENGING problems that extend concepts further and require deeper thinking and multiple steps.",
            "mixed": "Include a MIX OF DIFFICULTIES: Start with 2 easy problems, then 2 medium problems, and end with 1-2 challenging extension problems."
        }
        
        # Complete the prompt with formatting instructions
        prompt = base_prompt + f"""
        
        DIFFICULTY LEVEL: {difficulty.upper()}
        {difficulty_instructions.get(difficulty.lower(), difficulty_instructions["mixed"])}
        
        The worksheet should include:
        1. A title that clearly states the learning objective
        2. A brief introduction connecting to the lesson's content
        3. 3-5 practice problems that follow the EXACT same approach taught in the lesson
        4. Clear labels indicating the difficulty level of each problem (Easy, Medium, Hard)
        5. Space for students to show their work
        6. An answer key section for the teacher
        
        IMPORTANT: Ensure the worksheet follows the same instructional progression as the lesson plan,
        uses the same examples/methods demonstrated in class, and applies the same vocabulary.
        
        Format the worksheet as plain text.
        """
        
        try:
            # Call the OpenAI API to generate the worksheet
            response = self.config.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert mathematics educator specializing in creating aligned worksheets that reinforce classroom lessons exactly as they were taught."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating worksheet: {str(e)}"
    
    def refine(self, original_content, feedback, model="gpt-3.5-turbo"):
        """
        Refine an existing worksheet based on feedback.
        
        Improves the worksheet by incorporating specific feedback while 
        maintaining the original structure and purpose.
        
        Args:
            original_content (str): The original worksheet content
            feedback (str): Feedback or improvement suggestions
            model (str): The OpenAI model to use
            
        Returns:
            str: Refined worksheet content
        """
        try:
            # Create a prompt that preserves the structure but incorporates feedback
            prompt = f"""
            Please improve the following worksheet based on the provided feedback:
            
            ORIGINAL WORKSHEET:
            {original_content}
            
            FEEDBACK:
            {feedback}
            
            INSTRUCTIONS:
            1. Maintain the overall structure and format of the worksheet
            2. Address all points in the feedback
            3. Return the complete improved worksheet
            """
            
            # Call the API to refine the worksheet
            response = self.config.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert educator specializing in improving educational worksheets based on feedback."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error refining worksheet: {str(e)}"

#########################
# LESSON PLAN GENERATION MODULE
#########################

class LessonPlanGenerator:
    """
    Responsible for generating lesson plans following evidence-based instructional principles.
    
    This class creates detailed, standards-aligned lesson plans that follow 
    research-based pedagogical practices including explicit instruction, 
    gradual release of responsibility, and appropriate scaffolding.
    """
    def __init__(self, config_manager):
        """
        Initialize with configuration.
        
        Args:
            config_manager: ConfigManager instance for API access
        """
        self.config = config_manager
    
    def generate_plan(self, learning_outcome, grade, curriculum, duration, context, model="gpt-3.5-turbo"):
        """
        Generate a comprehensive lesson plan based on provided parameters.
        
        Creates a detailed lesson plan with clear learning objectives, instructional phases,
        and assessment strategies aligned with educational best practices. The lesson plan 
        follows the gradual release of responsibility model (I Do, We Do, You Do).
        
        Args:
            learning_outcome (str): The specific learning outcome
            grade (int/str): Grade level 
            curriculum (str): Curriculum standard name
            duration (str): Lesson duration (e.g., "45 minutes")
            context (str): Contextual information about the topic
            model (str): OpenAI model to use
            
        Returns:
            str: Generated lesson plan content
        """
        # Create a detailed prompt for structured lesson plan generation
        prompt = f"""
        Create a detailed lesson plan for teaching Grade {grade} mathematics according to {curriculum} standards.
        
        LEARNING OUTCOME:
        {learning_outcome}
        
        CONTEXT:
        {context}
        
        DURATION:
        {duration}
        
        INSTRUCTIONS:
        1. Include a clear lesson objective
        2. Provide a structured lesson outline following the Gradual Release of Responsibility model:
           - I Do (Teacher modeling)
           - We Do (Guided practice)
           - You Do (Independent practice)
        3. Include specific examples and activities
        4. Suggest assessment methods to evaluate student understanding
        5. Use appropriate vocabulary and notation for Grade {grade} students
        
        Format the lesson plan as plain text with clear section headings.
        """
        
        try:
            # Call the OpenAI API to generate the lesson plan
            response = self.config.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert mathematics educator specializing in creating detailed lesson plans for elementary education."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating lesson plan: {str(e)}"
    
    def refine(self, original_content, feedback, model="gpt-3.5-turbo"):
        """
        Refine an existing lesson plan based on feedback.
        
        Improves a lesson plan by incorporating specific feedback while 
        maintaining the original structure and purpose.
        
        Args:
            original_content (str): The original lesson plan
            feedback (str): Feedback or improvement suggestions
            model (str): The OpenAI model to use
            
        Returns:
            str: Refined lesson plan content
        """
        try:
            # Create a prompt that preserves the structure but incorporates feedback
            prompt = f"""
            Please improve the following lesson plan based on the provided feedback:
            
            ORIGINAL LESSON PLAN:
            {original_content}
            
            FEEDBACK:
            {feedback}
            
            INSTRUCTIONS:
            1. Maintain the overall structure and format of the lesson plan
            2. Address all points in the feedback
            3. Return the complete improved lesson plan
            """
            
            # Call the API to refine the lesson plan
            response = self.config.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert educator specializing in improving lesson plans based on teacher feedback."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error refining lesson plan: {str(e)}"

#########################
# DOCUMENT MANAGEMENT MODULE
#########################

class DocumentManager:
    """
    Manages document importing, parsing, and embedding for reference during content generation.
    """
    
    def __init__(self, config_manager):
        """Initialize with configuration."""
        self.config = config_manager
        self.documents = {}  # Dictionary to store document content by ID
        self.document_embeddings = {}  # Dictionary to store embeddings for RAG
    
    def import_document(self, file_path):
        """
        Import a document from file path and prepare it for reference.
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            str: Document ID for future reference or error message
        """
        try:
            doc_id = f"doc_{len(self.documents) + 1}"
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_ext == '.pdf':
                content = self._extract_text_from_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                content = self._extract_text_from_docx(file_path)
            else:
                return f"Error: Unsupported file format {file_ext}"
            
            self.documents[doc_id] = {
                "content": content,
                "path": file_path,
                "name": os.path.basename(file_path),
                "type": file_ext[1:]
            }
            
            return doc_id
        except Exception as e:
            return f"Error importing document: {str(e)}"
    
    def get_document_content(self, doc_id):
        """Get document content by ID."""
        return self.documents.get(doc_id, {}).get("content", "")
    
    def get_relevant_context(self, query, doc_ids=None, max_tokens=1000):
        """Use RAG to retrieve the most relevant portions of imported documents."""
        if not self.documents:
            return ""
            
        doc_ids = doc_ids or list(self.documents.keys())
        relevant_sections = []
        
        keywords = [k.lower() for k in query.split() if len(k) > 3]
        
        for doc_id in doc_ids:
            if doc_id not in self.documents:
                continue
                
            doc = self.documents[doc_id]
            content = doc["content"]
            paragraphs = content.split('\n\n')
            
            for paragraph in paragraphs:
                if any(keyword in paragraph.lower() for keyword in keywords):
                    relevant_sections.append(f"From {doc['name']}:\n{paragraph}")
                    
        context = "\n\n".join(relevant_sections)
        
        if len(context.split()) > max_tokens * 0.75:
            context = "\n\n".join(context.split('\n\n')[:5])
            
        return context
    
    def get_document_list(self):
        """Get a list of all imported documents."""
        return [
            {
                "doc_id": doc_id,
                "name": doc_info["name"],
                "type": doc_info.get("type", "unknown"),
                "size": len(doc_info["content"])
            }
            for doc_id, doc_info in self.documents.items()
        ]
    
    def remove_document(self, doc_id):
        """Remove a document by ID."""
        if doc_id in self.documents:
            del self.documents
            if doc_id in self.document_embeddings:
                del self.document_embeddings[doc_id]
            return True
        return False
    
    def _extract_text_from_pdf(self, file_path):
        """Extract text from PDF files (placeholder)."""
        return f"PDF text extraction placeholder for {file_path}"
    
    def _extract_text_from_docx(self, file_path):
        """Extract text from Word documents (placeholder)."""
        return f"DOCX text extraction placeholder for {file_path}"

#########################
# APPLICATION CONTROLLER
#########################

class LessonPlanController:
    """Central controller to coordinate operations and provide an API for UI layers."""
    def __init__(self, api_key=None):
        """Initialize the controller with optional API key."""
        self.config = ConfigManager(api_key)
        self.research = ResearchModule(self.config)
        self.generator = LessonPlanGenerator(self.config)
        self.worksheet_generator = WorksheetGenerator(self.config)
        self.document_manager = DocumentManager(self.config)
        
        self.model = "gpt-3.5-turbo"

    # CRITICAL BUG: Missing add_feedback method called in app_streamlit.py
    def add_feedback(self, content_id, feedback, content_type="lesson_plan"):
        """
        Store user feedback for a specific content.
        
        Args:
            content_id (str): Unique ID for the content
            feedback (str): User feedback text  
            content_type (str): Type of content ("lesson_plan" or "worksheet")
            
        Returns:
            bool: True if feedback was stored successfully
        """
        # In a full implementation this would store to a database
        # For now we'll just log it
        print(f"Feedback received for {content_type} {content_id}: {feedback[:50]}...")
        return True

    # CRITICAL BUG: _generate_pdf implementation doesn't match expected interface in app_streamlit.py
    def _generate_pdf(self, content, filename="lesson_plan.pdf", save_to_desktop=False):
        """Generate a PDF file from content."""
        try:
            # Determine the save location
            if save_to_desktop:
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                filename = os.path.join(desktop_path, filename)

            # Create a canvas object for the PDF
            c = canvas.Canvas(filename, pagesize=letter)
            c.setTitle("Educational Content")

            # Set font and starting position
            c.setFont("Helvetica", 12)
            width, height = letter
            x_margin = 50
            y_position = height - 50

            # Add title
            c.setFont("Helvetica-Bold", 16)
            title_text = "Educational Content"
            c.drawString(x_margin, y_position, title_text)
            y_position -= 30

            # Add content line by line with pagination
            c.setFont("Helvetica", 12)
            for line in content.split("\n"):
                # Start a new page if we're near the bottom
                if y_position < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = height - 50
                    
                # Handle long lines by wrapping - FIXED BUG: proper text wrapping
                if len(line) > 100:
                    chunks = [line[i:i+100] for i in range(0, len(line), 100)]
                    for chunk in chunks:
                        c.drawString(x_margin, y_position, chunk)
                        y_position -= 15
                else:
                    c.drawString(x_margin, y_position, line)
                    y_position -= 15

            # Save the PDF
            c.save()
            return filename
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return f"Error generating PDF: {str(e)}"

    def set_api_key(self, api_key):
        """Set or update the API key."""
        return self.config.set_api_key(api_key)

    def validate_api_key(self):
        """Check if API key is valid and configured."""
        return self.config.check_api_key()

    def get_research_data(self, grade, curriculum):
        """Get research data for a specific grade and curriculum."""
        try:
            return self.research.conduct_research(grade, curriculum, model=self.model)
        except Exception as e:
            return {"error": str(e)}

    def get_topics_list(self, research_data):
        """Extract topics list from research data."""
        if "error" in research_data:
            return []
        topics = []
        for idx, topic in enumerate(research_data.get("topics", [])):
            topics.append({
                "id": idx,
                "title": topic.get("title", ""),
                "description": topic.get("description", "")
            })
        return topics

    def get_learning_outcome(self, research_data, topic_id):
        """Get the learning outcome for a specific topic."""
        if "error" in research_data or not research_data.get("topics"):
            return {"error": "Invalid research data"}
        if topic_id < 0 or topic_id >= len(research_data["topics"]):
            return {"error": "Invalid topic ID"}
        return research_data["topics"][topic_id]

    def create_topic_context(self, topic_data):
        """Create a context string from topic data."""
        if "error" in topic_data:
            return ""
        context = f"""
        KEY CONCEPTS:
        {', '.join(topic_data.get('context', {}).get('key_concepts', []))}
        
        COMMON MISCONCEPTIONS:
        {', '.join(topic_data.get('context', {}).get('misconceptions', []))}
        
        PREREQUISITES:
        {', '.join(topic_data.get('context', {}).get('prerequisites', []))}
        
        TEACHING EXAMPLES:
        {', '.join(topic_data.get('context', {}).get('examples', []))}
        """
        return context

    def generate_lesson_plan(self, learning_outcome, grade, curriculum, duration, topic_context):
        """Generate a lesson plan with the specified parameters."""
        if not self.validate_api_key():
            return "Error: API key is missing or invalid"
        try:
            lesson_plan = self.generator.generate_plan(
                learning_outcome, grade, curriculum, duration, topic_context, model=self.model
            )
            return lesson_plan
        except Exception as e:
            return f"Error generating lesson plan: {str(e)}"

    def generate_worksheet(self, learning_outcome, topic_context, lesson_plan, difficulty="mixed"):
        """Generate a worksheet based on a lesson plan."""
        if not self.validate_api_key():
            return "Error: API key is missing or invalid"
        try:
            return self.worksheet_generator.generate_worksheet(
                learning_outcome=learning_outcome,
                context=topic_context,
                lesson_plan=lesson_plan,
                difficulty=difficulty,
                model=self.model
            )
        except Exception as e:
            return f"Error generating worksheet: {str(e)}"

    def save_as_pdf(self, content, filename=None, use_dialog=False, save_to_desktop=False):
        """Save content as PDF with optional file dialog."""
        try:
            if use_dialog:
                file_path = self._show_save_dialog(filename)
                if not file_path:
                    return "Canceled by user"
                self._generate_pdf(content, filename=file_path)
                return file_path
            else:
                filename = filename or "lesson_plan.pdf"
                self._generate_pdf(content, filename=filename, save_to_desktop=save_to_desktop)
                return filename
        except Exception as e:
            return f"Error saving PDF: {str(e)}"

    def _show_save_dialog(self, default_filename=None):
        """Show a file save dialog."""
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save as PDF",
                initialfile=default_filename or "lesson_plan.pdf"
            )
            return file_path or None
        except Exception:
            return None

    def _create_embeddings(self, doc_id):
        """Create embeddings for the document for future RAG use."""
        try:
            if doc_id not in self.documents:
                return
                
            content = self.documents[doc_id]["content"]
            
            # In production, would use OpenAI embeddings API
            # For placeholder implementation, just store document ID
            self.document_embeddings[doc_id] = f"placeholder_embedding_{doc_id}"
        except Exception as e:
            print(f"Warning: Could not create embeddings for {doc_id}: {e}")

    def get_document_list(self):
        """Get a list of all imported documents."""
        return [
            {
                "doc_id": doc_id,
                "name": doc_info["name"],
                "type": doc_info.get("type", "unknown"),
                "size": len(doc_info["content"])
            }
            for doc_id, doc_info in self.documents.items()
        ]

#########################
# MAIN APPLICATION
#########################

def run_console_app():
    """Run the application in console mode for backward compatibility."""
    controller = LessonPlanController()
    print("Welcome to the Modular Mathematics Lesson Plan Generator!")
    
    if not controller.validate_api_key():
        print("\nOpenAI API key is missing.")
        add_key = input("Would you like to add it now? (yes/no): ").strip().lower()
        if add_key in ["yes", "y"]:
            api_key = input("Enter your OpenAI API key: ").strip()
            controller.config.save_api_key_to_env(api_key)
    
    if not controller.validate_api_key():
        print("ERROR: OpenAI API key is required to run this application.")
        return
    
    try:
        grade = int(input("\nEnter Grade Level (1-5): "))
        curriculum = input("Enter Curriculum Standard: ").strip()
        duration = input("Enter Lesson Duration (e.g., '45 minutes'): ").strip()
        
        research_data = controller.get_research_data(grade, curriculum)
        if "error" in research_data:
            print(f"Error: {research_data['error']}")
            return
        
        topics = controller.get_topics_list(research_data)
        for idx, topic in enumerate(topics):
            print(f"{idx + 1}. {topic['title']} - {topic['description']}")
        
        topic_choice = int(input("\nSelect a topic by number: ")) - 1
        topic_data = controller.get_learning_outcome(research_data, topic_choice)
        learning_outcome = topic_data.get("learning_outcome", "")
        
        topic_context = controller.create_topic_context(topic_data)
        lesson_plan = controller.generate_lesson_plan(learning_outcome, grade, curriculum, duration, topic_context)
        
        print("\nGenerated Lesson Plan:")
        print(lesson_plan)
        
        save_choice = input("\nSave as PDF? (yes/no): ").strip().lower()
        if save_choice in ["yes", "y"]:
            controller.save_as_pdf(lesson_plan, "lesson_plan.pdf")
        
        worksheet_choice = input("\nGenerate Worksheet? (yes/no): ").strip().lower()
        if worksheet_choice in ["yes", "y"]:
            difficulty = input("Enter Difficulty (easy/medium/hard/mixed): ").strip().lower()
            worksheet = controller.generate_worksheet(learning_outcome, topic_context, lesson_plan, difficulty)
            print("\nGenerated Worksheet:")
            print(worksheet)
            
            save_choice = input("\nSave Worksheet as PDF? (yes/no): ").strip().lower()
            if save_choice in ["yes", "y"]:
                controller.save_as_pdf(worksheet, f"{difficulty}_worksheet.pdf")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_console_app()