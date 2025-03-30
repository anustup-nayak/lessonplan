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

# Set up OpenAI client using the API key from the environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def configure_api_keys():
    """
    Configure API keys if they're missing from the environment variables.
    """
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
        return True
    
    return False

def check_api_keys():
    """
    Check if API keys are properly loaded from environment variables.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print("\n--- API Key Status ---")
    print(f"OpenAI API Key: {'Available' if openai_key else 'Missing'}")
    
    if not openai_key:
        print("WARNING: OpenAI API key not found. Please check your .env file.")
    print("---------------------\n")
    
    return bool(openai_key)

def select_openai_model(purpose="general"):
    """
    Allow the user to select which OpenAI model to use for a specific purpose.
    
    Args:
        purpose (str): The purpose for which the model will be used
        
    Returns:
        str: The selected model name
    """
    # Updated model options with clearer compatibility information
    available_models = {
        1: {"name": "gpt-3.5-turbo", "description": "Fast, efficient, good for most tasks (4K context)"},
        2: {"name": "gpt-3.5-turbo-16k", "description": "Extended context for longer tasks (16K context)"},
        3: {"name": "gpt-4o", "description": "Latest GPT-4 model, best quality, JSON support (128K context)"},
        4: {"name": "gpt-4", "description": "High quality, best for complex tasks (8K context)"},
        5: {"name": "gpt-4-turbo", "description": "Fast version of GPT-4 with JSON support (128K context)"}
    }
    
    print(f"\nSelect OpenAI model to use for {purpose}:")
    for key, model_info in available_models.items():
        print(f"{key}. {model_info['name']} - {model_info['description']}")
    
    model_choice = get_numeric_input("Enter your choice: ", valid_range=range(1, len(available_models) + 1))
    selected_model = available_models[model_choice]["name"]
    print(f"Selected {selected_model} for {purpose}")
    return selected_model

def conduct_comprehensive_research(grade, curriculum, model="gpt-3.5-turbo-16k"):
    """
    Conduct comprehensive research on mathematics topics for a grade level,
    returning topics, learning outcomes, and contextual information in one step.
    
    Args:
        grade (int): Grade level (1-5)
        curriculum (str): Curriculum standards
        model (str): OpenAI model to use
        
    Returns:
        dict: Dictionary containing topics, selected topic, learning outcomes,
              selected outcome, and context information
    """
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
        json_models = ["gpt-4-turbo", "gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-3.5-turbo-0125"]
        
        if any(model_name in model for model_name in json_models):
            # Use JSON response format for supported models
            response = client.chat.completions.create(
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
            response = client.chat.completions.create(
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
    
    except Exception as e:
        print(f"Error conducting comprehensive research: {str(e)}")
        # Return a simplified structure if the research fails
        return {"topics": [
            {"title": "Addition", "description": "Basic addition operations", 
             "learning_outcome": "Add two-digit numbers", 
             "context": {"key_concepts": ["Place value", "Regrouping"], 
                        "misconceptions": ["Forgetting to regroup"], 
                        "prerequisites": ["Number recognition"], 
                        "examples": ["23 + 45 = 68"]}}
        ]}

def display_research_and_get_choices(research_data):
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

def generate_lesson_plan_with_context(topic, grade, curriculum, duration, context, model="gpt-3.5-turbo", summary_only=False):
    """
    Generate a lesson plan using the topic, grade level, curriculum and contextual information.
    
    Args:
        topic (str): The specific learning outcome
        grade (int): Grade level (1-5)
        curriculum (str): Curriculum standards to align with
        duration (str): Class duration (e.g., "45 minutes")
        context (str): Contextual information about the topic
        model (str): OpenAI model to use
        summary_only (bool): Whether to generate only a summary
        
    Returns:
        str: Generated lesson plan
    """
    if not (1 <= grade <= 5):
        return "Please provide a grade level between 1 and 5."
    
    # Convert duration to minutes
    try:
        total_minutes = int(duration.split()[0])
    except ValueError:
        return "Invalid duration format. Please specify the duration in minutes (e.g., '30 minutes')."
    
    # Calculate time allocations
    intro_time = max(5, int(0.15 * total_minutes))
    main_activity_time = max(10, int(0.5 * total_minutes))
    practice_time = max(5, int(0.2 * total_minutes))
    assessment_time = max(5, int(0.1 * total_minutes))
    conclusion_time = total_minutes - (intro_time + main_activity_time + practice_time + assessment_time)

    # Create the prompt with contextual information
    base_prompt = f"""
    Create a detailed mathematics lesson plan for Grade {grade} students on the topic: {topic}.
    
    Use the following contextual information to inform your lesson plan:
    {context}
    
    The lesson plan should include:
    1. Learning objectives
    2. Required materials
    3. Introduction to the topic ({intro_time} minutes)
    4. Main teaching activities ({main_activity_time} minutes)
    5. Practice exercises with examples ({practice_time} minutes)
    6. Assessment method ({assessment_time} minutes)
    7. Conclusion and homework assignment ({conclusion_time} minutes)
    
    Ensure the lesson plan incorporates the following pedagogical approaches:
    - **Concrete Pictorial Abstract (CPA) Approach**: Start with concrete examples, move to pictorial representations, and then to abstract concepts.
    - **Gradual Release of Responsibility (GRR)**: Use the "I do, we do, you do" model to gradually transfer responsibility to students.
    - **Rosenshine's Principles of Instruction**: Include principles such as reviewing prior knowledge, guided practice, checking for understanding, and providing scaffolding.
    - **Balance of Conceptual Understanding and Procedural Fluency**: Ensure students develop both a deep understanding of the concept and the ability to apply it fluently.
    - **Direct and Explicit Instruction**: Clearly explain concepts, model skills step-by-step, and provide guided practice before independent work.
    - **Worked Out Examples**: Include step-by-step solutions to problems to help students understand the process.
    - **Addressing Mathematical Misconceptions**: Identify common misconceptions related to the topic and include strategies to address them.
    - **Check for Understanding (CFU), Explanation, and Justification**: Incorporate methods to check for understanding and encourage students to explain and justify their reasoning.
    
    Additional Instructions:
    - Provide specific examples of problems posed by the teacher (e.g., add 34 + 67) and avoid generic ones (e.g., add two 2-digit numbers).
    - Make teacher instructions very specific and actionable.
    - Ensure the teacher uses the board for explanations and students work in their notebooks or on worksheets.
    
    The lesson duration is {duration}.
    
    Align the lesson plan with the following curriculum standards: {curriculum}.
    """
    
    # Adjust prompt for summary if needed
    if summary_only:
        prompt = base_prompt + "\n\nNow summarize the lesson plan into 1-2 sentences for each section."
    else:
        prompt = base_prompt
    
    try:
        # Call OpenAI API to generate the lesson plan
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an experienced mathematics teacher for elementary school."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000 if not summary_only else 1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating lesson plan: {str(e)}"

def enhance_lesson_plan_with_master_format(lesson_plan, topic, grade, model="gpt-3.5-turbo-16k"):
    """
    Enhance an existing lesson plan with the master lesson plan format.
    
    Args:
        lesson_plan (str): Original lesson plan content
        topic (str): The specific topic
        grade (int): Grade level
        model (str): OpenAI model to use
        
    Returns:
        str: Enhanced lesson plan following the master format
    """
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
        response = client.chat.completions.create(
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

# Function to generate a PDF file for the lesson plan
def generate_pdf(lesson_plan, filename="lesson_plan.pdf", save_to_desktop=False):
    """
    Generate a PDF file for the lesson plan.

    Args:
        lesson_plan (str): The content of the lesson plan.
        filename (str): The name of the PDF file to save.
        save_to_desktop (bool): Whether to save the file on the user's desktop.
    """
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
        print(f"Lesson plan successfully saved as {filename}")
    except Exception as e:
        print(f"An error occurred while generating the PDF: {e}")

def save_pdf_with_dialog(lesson_plan):
    """
    Open a save dialog to let the user choose where to save the PDF file.
    
    Args:
        lesson_plan (str): The content of the lesson plan.
    """
    try:
        print("Preparing to save PDF...")
        
        # Try to initialize tkinter root in a more robust way
        try:
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
            print(f"Generating PDF at: {file_path}")
            generate_pdf(lesson_plan, filename=file_path)
            print(f"Lesson plan successfully saved as {file_path}")
            
        except tk.TclError as e:
            print(f"Error with tkinter dialog: {e}")
            print("Saving PDF to default location instead...")
            generate_pdf(lesson_plan, filename="lesson_plan.pdf")
            print(f"Lesson plan saved as lesson_plan.pdf in the current directory")
            
    except Exception as e:
        print(f"An error occurred while saving the PDF: {e}")
        print("Attempting to save to default location...")
        try:
            generate_pdf(lesson_plan, filename="lesson_plan.pdf")
            print("Lesson plan saved as lesson_plan.pdf in the current directory")
        except Exception as e2:
            print(f"Could not save PDF: {e2}")

def save_pdf(lesson_plan):
    """
    Save the PDF without using a dialog (for environments where tkinter doesn't work).
    
    Args:
        lesson_plan (str): The content of the lesson plan.
    """
    try:
        filename = input("Enter filename for the PDF (default: lesson_plan.pdf): ").strip()
        if not filename:
            filename = "lesson_plan.pdf"
        
        # Ask if user wants to save to desktop
        desktop_choice = input("Save to desktop? (yes/no): ").lower()
        save_to_desktop = desktop_choice.startswith('y')
        
        generate_pdf(lesson_plan, filename=filename, save_to_desktop=save_to_desktop)
        
    except Exception as e:
        print(f"An error occurred while saving the PDF: {e}")
        print("Attempting to save to current directory...")
        try:
            generate_pdf(lesson_plan, filename="lesson_plan.pdf")
            print("Lesson plan saved as lesson_plan.pdf in the current directory")
        except Exception as e2:
            print(f"Could not save PDF: {e2}")

def get_numeric_input(prompt, valid_range=None):
    """
    Get numeric input from the user with validation.

    Args:
        prompt (str): The input prompt to display to the user.
        valid_range (range, optional): A range of valid numbers. Defaults to None.

    Returns:
        int: The validated numeric input.
    """
    while True:
        try:
            user_input = int(input(prompt))
            if valid_range and user_input not in valid_range:
                print(f"Invalid choice. Please enter a number between {valid_range.start} and {valid_range.stop - 1}.")
                continue
            return user_input
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    """
    Main function to run the app as a command-line application with enhanced integration.
    """
    print("Welcome to the Enhanced Mathematics Lesson Plan Generator!")
    
    # Configure API keys if missing
    configure_api_keys()
    
    # Check API keys
    openai_available = check_api_keys()
    if not openai_available:
        print("ERROR: OpenAI API key is required to run this application.")
        return
    
    print("\nWhich curriculum standards do you follow?")
    print("1. UK NCETM")
    print("2. US Common Core")
    print("3. Indian NCERT")
    print("4. Other")
    curriculum_choice = get_numeric_input("Enter the number corresponding to your curriculum: ", valid_range=range(1, 5))
    if curriculum_choice == 1:
        curriculum = "UK NCETM"
    elif curriculum_choice == 2:
        curriculum = "US Common Core"
    elif curriculum_choice == 3:
        curriculum = "Indian NCERT"
    elif curriculum_choice == 4:
        curriculum = input("Please specify your curriculum standards: ").strip()
    
    print("\nWhat is the duration of the class?")
    print("1. 30 minutes")
    print("2. 45 minutes")
    print("3. 60 minutes")
    print("4. Other")
    duration_choice = get_numeric_input("Enter the number corresponding to the class duration: ", valid_range=range(1, 5))
    if duration_choice == 1:
        duration = "30 minutes"
    elif duration_choice == 2:
        duration = "45 minutes"
    elif duration_choice == 3:
        duration = "60 minutes"
    elif duration_choice == 4:
        duration = input("Please specify the class duration: ").strip()
    
    grade = get_numeric_input("\nEnter Grade Level (1-5): ", valid_range=range(1, 6))
    
    model = select_openai_model("topic research")
    
    print(f"\nConducting comprehensive research for Grade {grade} aligned with the {curriculum} curriculum...")
    research_data = conduct_comprehensive_research(grade, curriculum, model)
    
    selected_topic, selected_outcome, topic_context = display_research_and_get_choices(research_data)
    
    print("\nGenerating lesson plan summary...")
    summary = generate_lesson_plan_with_context(
        selected_outcome, grade, curriculum, duration, topic_context, model, summary_only=True)
    
    print("\nLesson Plan Summary:")
    print(summary)
    
    print("\nDo you want to generate the full lesson plan?")
    print("1. Yes, generate full lesson plan")
    print("2. No, make changes")
    print("3. Exit")
    proceed_choice = get_numeric_input("Enter your choice: ", valid_range=range(1, 4))
    
    if proceed_choice == 1:
        print("\nGenerating full lesson plan...")
        lesson_plan = generate_lesson_plan_with_context(
            selected_outcome, grade, curriculum, duration, topic_context, model, summary_only=False)
        
        print("\nEnhancing lesson plan with structured format...")
        enhanced_lesson_plan = enhance_lesson_plan_with_master_format(
            lesson_plan, selected_outcome, grade, model)
        
        print("\nGenerated Enhanced Lesson Plan:")
        print(enhanced_lesson_plan)
        
        export_choice = input("\nDo you want to save the lesson plan as a PDF? (yes/no): ").strip().lower()
        if export_choice in ["yes", "y"]:
            try:
                save_pdf_with_dialog(enhanced_lesson_plan)
            except Exception as e:
                print(f"Dialog error: {e}. Falling back to console mode...")
                save_pdf(enhanced_lesson_plan)
    elif proceed_choice == 2:
        print("\nWhat would you like to change?")
        print("1. Select different learning outcome")
        print("2. Select different topic")
        print("3. Start over")
        change_choice = get_numeric_input("Enter your choice: ", valid_range=range(1, 4))
        
        if change_choice == 1:
            print("\nReturning to learning outcome selection...")
        elif change_choice == 2:
            print("\nReturning to topic selection...")
        else:
            print("\nRestarting the program...")
            main()
            return
    elif proceed_choice == 3:
        print("\nExiting. Goodbye!")
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting.")
    except ValueError:
        print("Invalid input. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")