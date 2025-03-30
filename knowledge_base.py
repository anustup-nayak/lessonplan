import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import time
from dotenv import load_dotenv
from knowledge_base import KnowledgeBase
import webbrowser
from urllib.parse import urlparse

class FileUploaderUI:
    """User interface for uploading files to the knowledge base."""
    
    def __init__(self, root, knowledge_base):
        """
        Initialize the file uploader UI.
        
        Args:
            root: Tkinter root window
            knowledge_base: KnowledgeBase instance
        """
        self.root = root
        self.kb = knowledge_base
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.root.title("Knowledge Base File Uploader")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tabs
        tab_control = ttk.Notebook(main_frame)
        
        # Local Files Tab
        local_tab = ttk.Frame(tab_control)
        tab_control.add(local_tab, text="Local Files")
        
        # URL Tab
        url_tab = ttk.Frame(tab_control)
        tab_control.add(url_tab, text="URLs")
        
        # Google Drive Tab
        gdrive_tab = ttk.Frame(tab_control)
        tab_control.add(gdrive_tab, text="Google Drive")
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Set up each tab
        self.setup_local_files_tab(local_tab)
        self.setup_url_tab(url_tab)
        self.setup_gdrive_tab(gdrive_tab)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
    def setup_local_files_tab(self, parent):
        """Set up the local files tab."""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Category selection
        ttk.Label(frame, text="Document Category:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.category_var = tk.StringVar(value="teaching_strategies")
        
        categories = [
            "teaching_strategies", 
            "curriculum_standards", 
            "lesson_plans", 
            "research", 
            "user_uploads"
        ]
        
        category_combo = ttk.Combobox(frame, textvariable=self.category_var, values=categories)
        category_combo.grid(row=0, column=1, sticky=tk.EW, pady=(0, 10), padx=(5, 0))
        
        # Grade selection
        ttk.Label(frame, text="Grade Level (optional):").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.grade_var = tk.StringVar()
        grade_combo = ttk.Combobox(frame, textvariable=self.grade_var, values=["", "1", "2", "3", "4", "5"])
        grade_combo.grid(row=1, column=1, sticky=tk.EW, pady=(0, 10), padx=(5, 0))
        
        # Curriculum selection
        ttk.Label(frame, text="Curriculum (optional):").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.curriculum_var = tk.StringVar()
        curricula = ["", "Common Core", "UK NCETM", "Indian NCERT"]
        curriculum_combo = ttk.Combobox(frame, textvariable=self.curriculum_var, values=curricula)
        curriculum_combo.grid(row=2, column=1, sticky=tk.EW, pady=(0, 10), padx=(5, 0))
        
        # Topic selection (for lesson plans)
        ttk.Label(frame, text="Topic (optional):").grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        self.topic_var = tk.StringVar()
        topic_entry = ttk.Entry(frame, textvariable=self.topic_var)
        topic_entry.grid(row=3, column=1, sticky=tk.EW, pady=(0, 10), padx=(5, 0))
        
        # Selected files list
        ttk.Label(frame, text="Selected Files:").grid(row=4, column=0, sticky=tk.W, pady=(0,# filepath: /workspaces/lessonplan/file_uploader.py

import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import time
from dotenv import load_dotenv
from knowledge_base import KnowledgeBase
import webbrowser
from urllib.parse import urlparse

class FileUploaderUI:
    """User interface for uploading files to the knowledge base."""
    
    def __init__(self, root, knowledge_base):
        """
        Initialize the file uploader UI.
        
        Args:
            root: Tkinter root window
            knowledge_base: KnowledgeBase instance
        """
        self.root = root
        self.kb = knowledge_base
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.root.title("Knowledge Base File Uploader")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tabs
        tab_control = ttk.Notebook(main_frame)
        
        # Local Files Tab
        local_tab = ttk.Frame(tab_control)
        tab_control.add(local_tab, text="Local Files")
        
        # URL Tab
        url_tab = ttk.Frame(tab_control)
        tab_control.add(url_tab, text="URLs")
        
        # Google Drive Tab
        gdrive_tab = ttk.Frame(tab_control)
        tab_control.add(gdrive_tab, text="Google Drive")
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Set up each tab
        self.setup_local_files_tab(local_tab)
        self.setup_url_tab(url_tab)
        self.setup_gdrive_tab(gdrive_tab)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
    def setup_local_files_tab(self, parent):
        """Set up the local files tab."""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Category selection
        ttk.Label(frame, text="Document Category:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.category_var = tk.StringVar(value="teaching_strategies")
        
        categories = [
            "teaching_strategies", 
            "curriculum_standards", 
            "lesson_plans", 
            "research", 
            "user_uploads"
        ]
        
        category_combo = ttk.Combobox(frame, textvariable=self.category_var, values=categories)
        category_combo.grid(row=0, column=1, sticky=tk.EW, pady=(0, 10), padx=(5, 0))
        
        # Grade selection
        ttk.Label(frame, text="Grade Level (optional):").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.grade_var = tk.StringVar()
        grade_combo = ttk.Combobox(frame, textvariable=self.grade_var, values=["", "1", "2", "3", "4", "5"])
        grade_combo.grid(row=1, column=1, sticky=tk.EW, pady=(0, 10), padx=(5, 0))
        
        # Curriculum selection
        ttk.Label(frame, text="Curriculum (optional):").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.curriculum_var = tk.StringVar()
        curricula = ["", "Common Core", "UK NCETM", "Indian NCERT"]
        curriculum_combo = ttk.Combobox(frame, textvariable=self.curriculum_var, values=curricula)
        curriculum_combo.grid(row=2, column=1, sticky=tk.EW, pady=(0, 10), padx=(5, 0))
        
        # Topic selection (for lesson plans)
        ttk.Label(frame, text="Topic (optional):").grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        self.topic_var = tk.StringVar()
        topic_entry = ttk.Entry(frame, textvariable=self.topic_var)
        topic_entry.grid(row=3, column=1, sticky=tk.EW, pady=(0, 10), padx=(5, 0))
        
        # Selected files list
        ttk.Label(frame, text="Selected Files:").grid(row=4, column=0, sticky=tk.W, pady=(0,