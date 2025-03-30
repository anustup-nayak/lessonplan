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
    
    def __init__(self):
        """Initialize configuration manager."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def configure_api_keys(self):
        """Configure API keys if they're missing from the environment variables."""
        updated = False
        env_path = os.path.join(os.getcwd(), '.env')
        
        # Check if .env file exists
        if not os.path.exists(env_path):
            with open(env_path, 'w') as f:
                f.write("# API Keys for Lesson Plan Generator\n")
        
        # Load existing variables
        with open(env_path, 'r') as f:
            env_contents = f.read()
        
        # Check OpenAI API key
        if "OPENAI_API_KEY" not in env_contents or not os.getenv("OPENAI_API_KEY"):
            print("\nOpenAI API key is missing.")
            add_key = input("Would you like to add it now? (yes/no): ").strip().lower()
            if add_key in ["yes", "y"]:
                api_key = input("Enter your OpenAI API key: ").strip()
                if "OPENAI_API_KEY" in env_contents:
                    env_contents = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={api_key}', env_contents)
                else:
                    env_contents += f"\nOPENAI_API_KEY={api_key}"
                updated = True
        
        # Save updated .env file if changes were made
        if updated:
            with open(env_path, 'w') as f:
                f.write(env_contents)
            print("API keys updated. Reloading environment variables...")
            load_dotenv(override=True)
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            return True
        
        return False
    
    def check_api_keys(self):
        """Check if API keys are properly loaded from environment variables."""
        openai_key = os.getenv("OPENAI_API_KEY")
        
        print("\n--- API Key Status ---")
        print(f"OpenAI API Key: {'Available' if openai_key else 'Missing'}")
        
        if not openai_key:
            print("WARNING: OpenAI API key not found. Please check your .env file.")
        print("---------------------\n")
        
        return bool(openai_key)
    
    def select_model(self, purpose="general"):
        """Allow user to select which OpenAI model to use for a specific purpose."""
        available_models = {
            1: {"name": "gpt-3.5-turbo", "description": "Fast, efficient, good balance (4K context)"},
            2: {"name": "gpt-3.5-turbo-16k", "description": "Extended context for longer tasks (16K)"},
            3: {"name": "gpt-4o", "description": "Latest GPT-4 model, best quality, JSON support"},
            4: {"name": "gpt-4", "description": "High quality for complex tasks"},
            5: {"name": "gpt-4-turbo", "description": "Fast GPT-4 with JSON support"}
        }
        
        print(f"\nSelect OpenAI model to use for {purpose}:")
        for key, model_info in available_models.items():
            print(f"{key}. {model_info['name']} - {model_info['description']}")
        
        model_choice = get_numeric_input("Enter your choice: ", valid_range=range(1, len(available_models) + 1))
        selected_model = available_models[model_choice]["name"]
        print(f"Selected {selected_model} for {purpose}")
        return selected_model

#########################
# RESEARCH MODULE
#########################

class ResearchModule:
    """Responsible for topic research and selection."""
    
    def __init__(self, config_manager):
        """Initialize with configuration."""
        self.config = config_manager
    
    def conduct_research(self, grade, curriculum, model="gpt-3.5-turbo-16k"):
        """Conduct comprehensive topic research."""
        print(f"\nConducting mathematics research for Grade {grade} ({curriculum})...")
        
        # Create a comprehensive research prompt
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
            
            # Check if the model supports JSON response format
            json_models = ["gpt-4o", "gpt-4-turbo", "gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-3.5-turbo-0125"]
            
            if any(model_name in model for model_name in json_models):
                # Use JSON response format for supported models
                response = self.config.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert mathematics curriculum specialist for elementary education."},
                        {"role": "user", "content": research_prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=4000,
                    temperature=0.7
                )
            else:
                # For models that don't support JSON response format
                response = self.config.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert mathematics curriculum specialist for elementary education. Respond ONLY with valid JSON."},
                        {"role": "user", "content": research_prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.7
                )
            
            # Extract the content and parse JSON
            content = response.choices[0].message.content
            
            # Try to find JSON in the response (even if the AI added extra text)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                research_data = json.loads(json_content)
            else:
                research_data = json.loads(content)  # Try parsing the whole response
                
            print(f"Successfully generated research on {len(research_data['topics'])} topics.")
            return research_data
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from API response: {str(e)}")
            print("API returned non-JSON content. Falling back to default topics.")
            # Return a simplified structure if JSON parsing fails
            return self._get_fallback_topics()
        
        except Exception as e:
            print(f"Error conducting comprehensive research: {str(e)}")
            # Return a simplified structure if the research fails
            return self._get_fallback_topics()
    
    def _get_fallback_topics(self):
        """Return fallback topics if research fails."""
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
    
    def display_topics_and_get_selection(self, research_data):
        """
        Display only topics and learning outcomes from research results.
        Context information is preserved but not shown to the user.
        
        Args:
            research_data (dict): Dictionary containing research data
        
        Returns:
            tuple: (selected_topic, selected_outcome, topic_context)
        """
        # Display topics
        print("\nHere are suggested mathematics topics:")
        for i, topic in enumerate(research_data["topics"], 1):
            print(f"{i}. {topic['title']} - {topic['description']}")
        
        # Get topic choice
        topic_choice = get_numeric_input("\nSelect a topic by number: ", valid_range=range(1, len(research_data["topics"]) + 1))
        selected_topic_data = research_data["topics"][topic_choice - 1]
        selected_topic = selected_topic_data["title"]
        
        print(f"\nYou selected: {selected_topic}")
        print(f"\nLearning outcome for this topic:")
        print(f"• {selected_topic_data['learning_outcome']}")
        
        # Create topic context string for internal use (not displayed)
        topic_context = f"""
        KEY CONCEPTS:
        {', '.join(selected_topic_data['context']['key_concepts'])}
        
        COMMON MISCONCEPTIONS:
        {', '.join(selected_topic_data['context']['misconceptions'])}
        
        PREREQUISITES:
        {', '.join(selected_topic_data['context']['prerequisites'])}
        
        TEACHING EXAMPLES:
        {', '.join(selected_topic_data['context']['examples'])}
        """
        
        # Confirm selection without showing context
        print("\nDo you want to use this learning outcome?")
        print("1. Yes, use this learning outcome")
        print("2. No, let me specify a custom learning outcome")
        outcome_choice = get_numeric_input("Enter your choice: ", valid_range=range(1, 3))
        
        if outcome_choice == 1:
            selected_outcome = selected_topic_data["learning_outcome"]
        else:
            selected_outcome = input("Enter your custom learning outcome: ").strip()
        
        return selected_topic, selected_outcome, topic_context

#########################
# LESSON PLAN GENERATION MODULE
#########################

class LessonPlanGenerator:
    """Responsible for generating lesson plans following evidence-based instructional principles."""
    
    def __init__(self, config_manager):
        """Initialize with configuration."""
        self.config = config_manager
    
    def generate_plan(self, topic, grade, curriculum, duration, context, model="gpt-3.5-turbo", summary_only=False):
        """
        Generate a comprehensive, structured lesson plan using research-based instructional approaches.
        
        Args:
            topic (str): The specific learning outcome or topic
            grade (int): Grade level (1-5)
            curriculum (str): Curriculum standards
            duration (str): Class duration (e.g., "45 minutes")
            context (str): Contextual information about the topic
            model (str): OpenAI model to use
            summary_only (bool): Whether to generate only a summary
            
        Returns:
            str: Generated lesson plan
        """
        if not (1 <= grade <= 5):
            return "Please provide a grade level between 1 and 5."
        
        # Calculate time allocations
        try:
            total_minutes = int(duration.split()[0])
            
            # Standard timing distribution
            warm_up_time = 5  # Standard 3-5 min
            intro_time = 5
            modeling_time = 10
            guided_practice_time = 8
            independent_time = 8
            extension_time = max(5, int(0.1 * total_minutes))
            exit_ticket_time = 5
            
            # Adjust if time is very limited
            if total_minutes < 40:
                modeling_time = max(8, int(0.25 * total_minutes))
                guided_practice_time = max(7, int(0.2 * total_minutes))
                independent_time = max(7, int(0.2 * total_minutes))
                
            # Adjust if time is extended
            if total_minutes > 60:
                independent_time = max(10, int(0.25 * total_minutes))
                extension_time = max(8, int(0.15 * total_minutes))
                
        except ValueError:
            # Default timings if duration parsing fails
            warm_up_time = 5
            intro_time = 5
            modeling_time = 10
            guided_practice_time = 8
            independent_time = 8
            extension_time = 5
            exit_ticket_time = 5
        
        # Create the enhanced lesson plan prompt with structured format
        base_prompt = self._create_enhanced_lesson_plan_prompt(
            topic, grade, curriculum, duration, context,
            warm_up_time, intro_time, modeling_time, guided_practice_time, 
            independent_time, extension_time, exit_ticket_time
        )
        
        # For summary, add additional instruction
        if summary_only:
            prompt = base_prompt + "\n\nProvide just a brief 1-2 sentence summary for each main section of the lesson plan."
        else:
            prompt = base_prompt
        
        try:
            # Call OpenAI API to generate the lesson plan
            response = self.config.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert mathematics educator with experience in elementary education, cognitive science research, and evidence-based instructional design."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3500 if not summary_only else 1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating lesson plan: {str(e)}"
    
    def _create_enhanced_lesson_plan_prompt(self, topic, grade, curriculum, duration, context,
                                           warm_up_time, intro_time, modeling_time, guided_practice_time,
                                           independent_time, extension_time, exit_ticket_time):
        """
        Create a comprehensive lesson plan prompt using the master lesson plan format.
        
        Args:
            topic (str): The specific learning outcome or topic
            grade (int): Grade level
            curriculum (str): Curriculum standards
            duration (str): Class duration
            context (str): Contextual information about the topic
            warm_up_time (int): Time for warm-up activities
            intro_time (int): Time for introduction
            modeling_time (int): Time for explicit modeling
            guided_practice_time (int): Time for guided practice
            independent_time (int): Time for independent practice
            extension_time (int): Time for extension activities
            exit_ticket_time (int): Time for assessment/exit ticket
            
        Returns:
            str: The formatted lesson plan prompt
        """
        return f"""
        Create a detailed, classroom-ready mathematics lesson plan for Grade {grade} on the topic: {topic}.
        
        Use the following contextual information to enrich your lesson plan:
        {context}
        
        ✅ LESSON PLAN FORMAT
        
        1. Lesson Title & Grade Level
           Title should specify the exact math focus and learning domain (e.g., Grade {grade}: {topic})
        
        2. Learning Objective(s)
           - Aligned with {curriculum} standards
           - Include BOTH procedural goal (what students will DO) and conceptual goal (what students will UNDERSTAND)
        
        3. Prerequisite Knowledge
           - List 3-4 specific skills and concepts students should already have mastered
           - Be specific about the level of fluency expected (e.g., "automatic recall of addition facts to 10")
        
        4. Materials
           Include tools that support the CPA approach:
           - Concrete manipulatives (physical objects)
           - Pictorial representations (diagrams, charts)
           - Abstract tools (worksheets, algorithms)
        
        5. Common Misconceptions
           - Identify 2-3 specific errors students typically make with this content
           - Include precise teacher language to address each misconception
        
        📈 INSTRUCTIONAL PHASES
        
        A. Daily Warm-Up / Activation of Prior Knowledge ({warm_up_time} min)
           - Begin with a specific review activity or retrieval practice
           - Include 2-3 example problems or questions with answers
        
        B. Introduction ({intro_time} min)
           - Present a problem that highlights the need for today's skill
           - Include specific questions the teacher should ask
           - Connect to real-world applications when possible
        
        C. I Do (Explicit Modeling, {modeling_time} min)
           - Start with concrete manipulatives (e.g., base-10 blocks)
           - Transition to pictorial representations (e.g., diagrams)
           - End with abstract procedures (e.g., algorithms, formulas)
           - Include EXACT teacher language in quotation marks
           - Write out step-by-step instructions for working through 1-2 example problems
        
        D. We Do (Guided Practice, {guided_practice_time} min)
           - Include 1-2 problems to solve together with decreasing support
           - Write specific questions to check for understanding
           - Provide clear guidance on how to structure student participation
        
        E. You Do (Independent Practice, {independent_time} min)
           - Provide 3-5 appropriate practice problems with answers
           - Include directions for differentiation (support and extension)
           - Specify how the teacher should monitor and give feedback
        
        F. Practice Extension ({extension_time} min)
           - Include 1-2 challenging problems that extend the skill
           - Describe how to structure pair/group work if applicable
        
        G. Exit Ticket ({exit_ticket_time} min)
           - Provide 1-2 specific assessment questions with answers
           - Include criteria for evaluating student mastery
        
        The full lesson duration is {duration}. Follow these additional requirements:
        
        - Follow explicit instruction principles with clear teacher language
        - Incorporate the CPA (Concrete-Pictorial-Abstract) approach in sequence
        - Integrate Rosenshine's Principles of Instruction (daily review, small steps, modeling, guided practice, checks for understanding)
        - Balance conceptual understanding and procedural fluency
        - Provide SPECIFIC examples (e.g., "34 + 67" not "two-digit addition")
        - Include explicit teacher instructions and scripts
        - Use clear transitions between lesson phases
        
        Use precise teacher language, avoid vague instructions like "try your best," and instead use specific directives like "line up your digits carefully."
        
        Align all aspects of the lesson with {curriculum} standards for Grade {grade} mathematics.
        """

#########################
# LESSON PLAN FORMATTING MODULE
#########################

class LessonPlanFormatter:
    """Responsible for formatting and exporting lesson plans."""
    
    def __init__(self, config_manager):
        """Initialize with configuration."""
        self.config = config_manager
    
    def enhance_with_master_format(self, lesson_plan, topic, grade, model="gpt-3.5-turbo-16k"):
        """Enhance an existing lesson plan with the master format."""
        prompt = f"""
        Reformat and enhance the following mathematics lesson plan to follow this precise structure:
        
        ✅ LESSON PLAN FORMAT
        1. Lesson Title & Grade Level: Grade {grade}: {topic}
        2. Learning Objective(s) - Include both procedural and conceptual goals
        3. Prerequisite Knowledge - List relevant skills and concepts students should already have
        4. Materials - Include tools that support CPA learning
        5. Common Misconceptions - Identify 2-3 predictable student errors

        📈 INSTRUCTIONAL PHASES
        A. Daily Warm-Up / Activation of Prior Knowledge (3-5 min)
        B. Introduction (5 min)
        C. I Do (Explicit Modeling, 8-10 min)
        D. We Do (Guided Practice, 8 min)
        E. You Do (Independent Practice, 8 min)
        F. Practice Extension (5-8 min)
        G. Exit Ticket (3-5 min)
        
        Here is the original lesson plan to enhance:
        {lesson_plan}
        
        Make sure the enhanced plan follows explicit instruction principles, incorporates the CPA approach, 
        and integrates Rosenshine's Principles. Use specific examples and clear teacher instructions.
        """
        
        try:
            response = self.config.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an experienced mathematics teacher for elementary school."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error enhancing lesson plan: {str(e)}")
            return lesson_plan  # Return original if enhancement fails
    
    def export_as_pdf(self, lesson_plan):
        """Export the lesson plan as PDF with dialog."""
        try:
            # Try to initialize tkinter root
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Make sure the dialog window appears on top
            root.attributes('-topmost', True)
            
            # Open the save dialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Lesson Plan as PDF",
                initialfile="lesson_plan.pdf"
            )
            
            # If the user cancels, file_path will be empty
            if not file_path:
                print("Save operation canceled.")
                return
            
            # Generate the PDF at the selected location
            self._generate_pdf(lesson_plan, filename=file_path)
            print(f"Lesson plan successfully saved as {file_path}")
            
        except Exception as e:
            print(f"Dialog error: {e}. Falling back to console mode...")
            self._save_pdf_console(lesson_plan)
    
    def _save_pdf_console(self, lesson_plan):
        """Save PDF via console input (fallback)."""
        try:
            filename = input("Enter filename for the PDF (default: lesson_plan.pdf): ").strip()
            if not filename:
                filename = "lesson_plan.pdf"
            
            # Ask if user wants to save to desktop
            desktop_choice = input("Save to desktop? (yes/no): ").lower()
            save_to_desktop = desktop_choice.startswith('y')
            
            self._generate_pdf(lesson_plan, filename=filename, save_to_desktop=save_to_desktop)
            
        except Exception as e:
            print(f"An error occurred while saving the PDF: {e}")
            try:
                self._generate_pdf(lesson_plan, filename="lesson_plan.pdf")
                print("Lesson plan saved as lesson_plan.pdf in the current directory")
            except Exception as e2:
                print(f"Could not save PDF: {e2}")
    
    def _generate_pdf(self, lesson_plan, filename="lesson_plan.pdf", save_to_desktop=False):
        """Generate a PDF file for the lesson plan."""
        try:
            # Determine the save location
            if save_to_desktop:
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                filename = os.path.join(desktop_path, filename)

            # Create a canvas object for the PDF
            pdf = canvas.Canvas(filename, pagesize=letter)
            pdf.setTitle("Lesson Plan")

            # Set font and starting position
            pdf.setFont("Helvetica", 12)
            width, height = letter
            x_margin = 50
            y_position = height - 50

            # Add title
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(x_margin, y_position, "Mathematics Lesson Plan")
            y_position -= 30

            # Add content line by line
            pdf.setFont("Helvetica", 12)
            for line in lesson_plan.split("\n"):
                if y_position < 50:  # Start a new page if the content exceeds the page height
                    pdf.showPage()
                    pdf.setFont("Helvetica", 12)
                    y_position = height - 50
                pdf.drawString(x_margin, y_position, line)
                y_position -= 15

            # Save the PDF
            pdf.save()
            print(f"Lesson plan saved as {filename}")
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise

#########################
# USER INTERACTION MODULE
#########################

class UserInteractionManager:
    """Manages user interactions and workflow."""
    
    def __init__(self):
        """Initialize the user interaction manager."""
        self.config = ConfigManager()
        self.research = ResearchModule(self.config)
        self.generator = LessonPlanGenerator(self.config)
        self.formatter = LessonPlanFormatter(self.config)
    
    def run(self):
        """Run the main application workflow."""
        print("Welcome to the Modular Mathematics Lesson Plan Generator!")
        
        # Configure API keys if missing
        self.config.configure_api_keys()
        
        # Check API keys
        if not self.config.check_api_keys():
            print("ERROR: OpenAI API key is required to run this application.")
            return
        
        try:
            # Get curriculum standards
            curriculum = self._get_curriculum()
            
            # Get class duration
            duration = self._get_duration()
            
            # Get grade level
            grade = get_numeric_input("\nEnter Grade Level (1-5): ", valid_range=range(1, 6))
            
            # Model selection
            model = self.config.select_model("topic research")
            
            # Research Phase
            research_data = self.research.conduct_research(grade, curriculum, model)
            selected_topic, selected_outcome, topic_context = self.research.display_topics_and_get_selection(research_data)
            
            # Let user know contextual information is being used
            print("\nAdditional contextual information about this topic (key concepts, misconceptions, etc.) will be used in generating the lesson plan.")
            
            # Generate summary
            print("\nGenerating lesson plan summary...")
            summary = self.generator.generate_plan(
                selected_outcome, grade, curriculum, duration, topic_context, model, summary_only=True)
            
            print("\nLesson Plan Summary:")
            print(summary)
            
            # Ask to proceed with full plan
            proceed_choice = self._ask_to_proceed()
            
            if proceed_choice == 1:
                # Generate full lesson plan
                self._generate_full_plan(selected_outcome, grade, curriculum, duration, topic_context, model)
            elif proceed_choice == 2:
                # Make changes
                self._handle_changes(grade, curriculum, research_data)
            else:
                print("\nExiting. Goodbye!")
                return
                
        except KeyboardInterrupt:
            print("\nOperation interrupted. Exiting.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
    def _get_curriculum(self):
        """Get curriculum choice from user."""
        print("\nWhich curriculum standards do you follow?")
        print("1. UK NCETM")
        print("2. US Common Core")
        print("3. Indian NCERT")
        print("4. Other")
        curriculum_choice = get_numeric_input("Enter the number corresponding to your curriculum: ", valid_range=range(1, 5))
        if curriculum_choice == 1:
            return "UK NCETM"
        elif curriculum_choice == 2:
            return "US Common Core"
        elif curriculum_choice == 3:
            return "Indian NCERT"
        else:
            return input("Please specify your curriculum standards: ").strip()
    
    def _get_duration(self):
        """Get class duration from user."""
        print("\nWhat is the duration of the class?")
        print("1. 30 minutes")
        print("2. 45 minutes")
        print("3. 60 minutes")
        print("4. Other")
        duration_choice = get_numeric_input("Enter the number corresponding to the class duration: ", valid_range=range(1, 5))
        if duration_choice == 1:
            return "30 minutes"
        elif duration_choice == 2:
            return "45 minutes"
        elif duration_choice == 3:
            return "60 minutes"
        else:
            return input("Please specify the class duration: ").strip()
    
    def _ask_to_proceed(self):
        """Ask user if they want to proceed with full plan generation."""
        print("\nDo you want to generate the full lesson plan?")
        print("1. Yes, generate full lesson plan")
        print("2. No, make changes")
        print("3. Exit")
        return get_numeric_input("Enter your choice: ", valid_range=range(1, 4))
    
    def _generate_full_plan(self, selected_outcome, grade, curriculum, duration, topic_context, model):
        """Generate and format the full lesson plan."""
        print("\nGenerating full lesson plan...")
        print("(Using topic context information for enhanced quality)")
        lesson_plan = self.generator.generate_plan(
            selected_outcome, grade, curriculum, duration, topic_context, model, summary_only=False)
        
        # Enhance the lesson plan
        print("\nEnhancing lesson plan with structured format...")
        enhanced_lesson_plan = self.formatter.enhance_with_master_format(
            lesson_plan, selected_outcome, grade, model)
        
        print("\nGenerated Enhanced Lesson Plan:")
        print(enhanced_lesson_plan)
        
        # Export option
        export_choice = input("\nDo you want to save the lesson plan as a PDF? (yes/no): ").strip().lower()
        if export_choice in ["yes", "y"]:
            self.formatter.export_as_pdf(enhanced_lesson_plan)
    
    def _handle_changes(self, grade, curriculum, research_data):
        """Handle user-requested changes to the plan."""
        print("\nWhat would you like to change?")
        print("1. Select different learning outcome")
        print("2. Select different topic")
        print("3. Start over")
        change_choice = get_numeric_input("Enter your choice: ", valid_range=range(1, 4))
        
        if change_choice == 1:
            print("\nReturning to learning outcome selection...")
            # This would implement re-selection logic
        elif change_choice == 2:
            print("\nReturning to topic selection...")
            # This would implement re-selection logic
        else:
            print("\nRestarting the program...")
            self.run()

#########################
# HELPER FUNCTIONS
#########################

def get_numeric_input(prompt, valid_range=None):
    """
    Get numeric input from the user with validation.
    
    Args:
        prompt (str): The prompt to display to the user.
        valid_range (range, optional): Range of valid values.
        
    Returns:
        int: The validated numeric input.
    """
    while True:
        try:
            value = int(input(prompt))
            if valid_range and value not in valid_range:
                print(f"Please enter a value between {valid_range.start} and {valid_range.stop - 1}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")

#########################
# MAIN APPLICATION
#########################

if __name__ == "__main__":
    try:
        app = UserInteractionManager()
        app.run()
    except KeyboardInterrupt:
        print("\nProgram terminated by user. Goodbye!")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")