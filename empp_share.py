import gradio as gr
import PyPDF2
import requests
import json
import pandas as pd
import io
from typing import Dict, List, Optional, Tuple
import re
import os
from datetime import datetime

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama2"  # Change this to your preferred model

class EmployeeAnalyzer:
    def __init__(self):
        self.company_name = "CGVAK SOFTWARE&EXPORTS"
        
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            if pdf_file is None:
                return ""
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def test_ollama_connection(self) -> Tuple[str, bool]:
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                return f"✅ Connected! Available models: {', '.join(model_names)}", True
            else:
                return "❌ Ollama connection failed!", False
        except Exception as e:
            return f"❌ Cannot connect to Ollama: {str(e)}. Make sure it's running on localhost:11434", False
    
    def query_ollama(self, prompt: str, model: str = None) -> str:
        """Send query to Ollama model"""
        try:
            model_to_use = model if model else MODEL_NAME
            url = f"{OLLAMA_BASE_URL}/api/generate"
            data = {
                "model": model_to_use,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=60)
            if response.status_code == 200:
                return response.json().get('response', 'No response from model')
            else:
                return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
    
    def extract_employee_info(self, text: str, employee_name: str, model: str = None) -> str:
        """Extract specific employee information using Ollama"""
        if not text:
            return "No text available. Please upload a PDF file first."
        
        if not employee_name:
            return "Please enter an employee name to search."
        
        prompt = f"""
        Analyze the following employee report text and extract information about employee named "{employee_name}" 
        from {self.company_name}. 
        
        Please provide the information in this exact format:
        
        🏢 COMPANY: {self.company_name}
        👤 EMPLOYEE DETAILS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📝 Name: [Employee Name]
        🆔 Employee ID: [ID if available]
        🏛️  Department: [Department]
        💼 Position: [Job Title/Position]
        💰 Salary: [Salary information if available]
        📅 Joining Date: [Date if available]
        ⭐ Performance: [Performance details if available]
        📞 Contact: [Contact information if available]
        📧 Email: [Email if available]
        🏠 Address: [Address if available]
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        If any information is not available, write "Not Available"
        If the employee is not found, clearly state "Employee not found in the report"
        
        Employee Report Text:
        {text[:3000]}...
        """
        
        return self.query_ollama(prompt, model)
    
    def search_all_employees(self, text: str, model: str = None) -> str:
        """Get list of all employees in the report"""
        if not text:
            return "No text available. Please upload a PDF file first."
        
        prompt = f"""
        Analyze the following employee report from {self.company_name} and list all employee names mentioned.
        
        Format the response as:
        
        🏢 {self.company_name}
        👥 EMPLOYEES FOUND IN REPORT:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        1. [Employee Name 1]
        2. [Employee Name 2]
        3. [Employee Name 3]
        4. [Employee Name 4]
        ... and so on
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        Total Employees Found: [Number]
        
        If no employees are found, state "No employee names found in the report"
        
        Employee Report Text:
        {text[:3000]}...
        """
        
        return self.query_ollama(prompt, model)

# Initialize analyzer
analyzer = EmployeeAnalyzer()

# Global variable to store extracted text
extracted_text = ""

def process_pdf(pdf_file):
    """Process uploaded PDF and extract text"""
    global extracted_text
    
    if pdf_file is None:
        return "Please upload a PDF file.", ""
    
    extracted_text = analyzer.extract_text_from_pdf(pdf_file)
    
    if "Error" in extracted_text:
        return extracted_text, ""
    
    preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
    return f"✅ PDF processed successfully! Extracted {len(extracted_text)} characters.", preview

def search_employee(employee_name, model_choice):
    """Search for specific employee"""
    global extracted_text
    
    if not extracted_text:
        return "Please upload and process a PDF file first."
    
    result = analyzer.extract_employee_info(extracted_text, employee_name, model_choice)
    return result

def get_all_employees(model_choice):
    """Get all employees from the report"""
    global extracted_text
    
    if not extracted_text:
        return "Please upload and process a PDF file first."
    
    result = analyzer.search_all_employees(extracted_text, model_choice)
    return result

def test_connection():
    """Test Ollama connection"""
    status, connected = analyzer.test_ollama_connection()
    return status

def create_gradio_interface():
    """Create the Gradio interface"""
    
    # Custom CSS for better styling
    css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    .company-header {
        text-align: center;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    """
    
    with gr.Blocks(css=css, title="CGVAK Employee Analyzer", theme=gr.themes.Soft()) as app:
        
        # Header
        gr.HTML("""
        <div class="company-header">
            <h1>🏢 CGVAK SOFTWARE&EXPORTS</h1>
            <h2>Employee Report Analyzer</h2>
            <p>AI-Powered Employee Information System | Accessible Worldwide 🌍</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## ⚙️ Configuration")
                
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=["llama2", "llama3", "mistral", "codellama", "neural-chat"],
                    value="llama2",
                    label="Select AI Model",
                    info="Choose the Ollama model for analysis"
                )
                
                # Connection test
                connection_btn = gr.Button("🔗 Test Ollama Connection", variant="secondary")
                connection_status = gr.Textbox(
                    label="Connection Status",
                    interactive=False,
                    lines=2
                )
                
                connection_btn.click(
                    test_connection,
                    outputs=connection_status
                )
            
            with gr.Column(scale=2):
                gr.Markdown("## 📄 Upload Employee Report")
                
                # File upload
                pdf_upload = gr.File(
                    label="Upload PDF Report",
                    file_types=[".pdf"],
                    type="filepath"
                )
                
                process_btn = gr.Button("📊 Process PDF", variant="primary")
                
                # Processing status and preview
                process_status = gr.Textbox(
                    label="Processing Status",
                    interactive=False,
                    lines=2
                )
                
                text_preview = gr.Textbox(
                    label="Text Preview",
                    interactive=False,
                    lines=5,
                    placeholder="Extracted text will appear here..."
                )
                
                process_btn.click(
                    process_pdf,
                    inputs=pdf_upload,
                    outputs=[process_status, text_preview]
                )
        
        gr.Markdown("---")
        
        # Search section
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🔍 Search Employee")
                
                employee_input = gr.Textbox(
                    label="Employee Name",
                    placeholder="Enter employee name (e.g., John Doe)",
                    lines=1
                )
                
                search_btn = gr.Button("🔍 Search Employee", variant="primary")
                
                employee_result = gr.Textbox(
                    label="Employee Details",
                    interactive=False,
                    lines=15,
                    placeholder="Employee information will appear here..."
                )
                
                search_btn.click(
                    search_employee,
                    inputs=[employee_input, model_dropdown],
                    outputs=employee_result
                )
            
            with gr.Column():
                gr.Markdown("## 👥 All Employees")
                
                all_employees_btn = gr.Button("📋 Get All Employees", variant="secondary")
                
                all_employees_result = gr.Textbox(
                    label="All Employees List",
                    interactive=False,
                    lines=15,
                    placeholder="Complete employee list will appear here..."
                )
                
                all_employees_btn.click(
                    get_all_employees,
                    inputs=model_dropdown,
                    outputs=all_employees_result
                )
        
        # Usage instructions
        gr.Markdown("""
        ---
        ## 📖 How to Use:
        
        1. **Setup**: Make sure Ollama is running locally with a model installed
        2. **Test Connection**: Click "Test Ollama Connection" to verify setup
        3. **Upload PDF**: Upload your employee report PDF file
        4. **Process**: Click "Process PDF" to extract text
        5. **Search**: Enter employee name and click "Search Employee"
        6. **View All**: Click "Get All Employees" to see complete list
        
        ## 🌐 Sharing:
        This application can be accessed by anyone with the public link!
        
        ## 🔧 Technical Requirements:
        - Ollama must be running on the host machine
        - Supported models: llama2, llama3, mistral, codellama
        - PDF files should contain readable text (not scanned images)
        """)
        
        # Footer
        gr.HTML("""
        <div style='text-align: center; margin-top: 30px; padding: 20px; background-color: #f0f0f0; border-radius: 10px;'>
            <h3>🏢 CGVAK SOFTWARE&EXPORTS</h3>
            <p><strong>Employee Report Analyzer</strong></p>
            <p>Powered by Gradio + Ollama + PyPDF2 | Accessible Worldwide 🌍</p>
            <p><em>Generated on: {}</em></p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    return app

def main():
    """Main function to launch the application"""
    app = create_gradio_interface()
    
    # Launch with public sharing enabled
    app.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,       # Default Gradio port
        share=True,             # Create public link
        debug=True,             # Enable debug mode
        show_error=True,        # Show errors
        inbrowser=True,         # Open in browser automatically
        # auth=("admin", "password123"),  # Uncomment to add authentication
    )

if __name__ == "__main__":
    main()