import streamlit as st
import PyPDF2
import requests
import json
import pandas as pd
import io
from typing import Dict, List, Optional
import re

# Configure Streamlit page
st.set_page_config(
    page_title="CGVAK Employee Report Analyzer",
    page_icon="👥",
    layout="wide"
)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama2"  # Change this to your preferred model

class EmployeeAnalyzer:
    def __init__(self):
        self.company_name = "CGVAK SOFTWARE&EXPORTS"
        
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def query_ollama(self, prompt: str) -> str:
        """Send query to Ollama model"""
        try:
            url = f"{OLLAMA_BASE_URL}/api/generate"
            data = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                return response.json().get('response', 'No response from model')
            else:
                return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
    
    def extract_employee_info(self, text: str, employee_name: str) -> Dict:
        """Extract specific employee information using Ollama"""
        prompt = f"""
        Analyze the following employee report text and extract information about employee named "{employee_name}" 
        from {self.company_name}. 
        
        Please provide the information in this exact format:
        Name: [Employee Name]
        Employee ID: [ID if available]
        Department: [Department]
        Position: [Job Title/Position]
        Salary: [Salary information if available]
        Joining Date: [Date if available]
        Performance: [Performance details if available]
        Contact: [Contact information if available]
        
        If any information is not available, write "Not Available"
        
        Employee Report Text:
        {text}
        """
        
        return self.query_ollama(prompt)
    
    def search_all_employees(self, text: str) -> str:
        """Get list of all employees in the report"""
        prompt = f"""
        Analyze the following employee report from {self.company_name} and list all employee names mentioned.
        
        Format the response as:
        EMPLOYEES FOUND:
        1. [Employee Name 1]
        2. [Employee Name 2]
        3. [Employee Name 3]
        ... and so on
        
        Employee Report Text:
        {text}
        """
        
        return self.query_ollama(prompt)

def main():
    st.title("🏢 CGVAK SOFTWARE&EXPORTS")
    st.header("Employee Report Analyzer")
    st.markdown("---")
    
    # Initialize analyzer
    analyzer = EmployeeAnalyzer()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        model_options = ["llama2", "llama3", "mistral", "codellama"]
        selected_model = st.selectbox("Select Ollama Model:", model_options)
        MODEL_NAME = selected_model
        
        # Ollama connection test
        if st.button("Test Ollama Connection"):
            try:
                response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Ollama is connected!")
                else:
                    st.error("❌ Ollama connection failed!")
            except:
                st.error("❌ Cannot connect to Ollama. Make sure it's running on localhost:11434")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📄 Upload Employee Report")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF file", 
            type="pdf",
            help="Upload the employee report PDF file"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Extract text from PDF
            with st.spinner("Extracting text from PDF..."):
                pdf_text = analyzer.extract_text_from_pdf(uploaded_file)
            
            if pdf_text:
                st.success("✅ Text extracted successfully!")
                
                # Show preview of extracted text
                with st.expander("Preview Extracted Text"):
                    st.text_area("", pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text, height=200)
                
                # Store text in session state
                st.session_state['pdf_text'] = pdf_text
                
                # Button to show all employees
                if st.button("🔍 Show All Employees", type="secondary"):
                    with st.spinner("Analyzing employee data..."):
                        all_employees = analyzer.search_all_employees(pdf_text)
                        st.session_state['all_employees'] = all_employees
    
    with col2:
        st.subheader("🔍 Employee Search")
        
        if 'pdf_text' in st.session_state:
            # Employee name input
            employee_name = st.text_input(
                "Enter Employee Name:",
                placeholder="e.g., John Doe",
                help="Enter the full name or partial name of the employee"
            )
            
            # Search button
            if st.button("🔍 Search Employee", type="primary"):
                if employee_name:
                    with st.spinner(f"Searching for {employee_name}..."):
                        employee_info = analyzer.extract_employee_info(
                            st.session_state['pdf_text'], 
                            employee_name
                        )
                        st.session_state['employee_info'] = employee_info
                        st.session_state['searched_name'] = employee_name
                else:
                    st.warning("Please enter an employee name to search.")
            
            # Display search results
            if 'employee_info' in st.session_state:
                st.markdown("### 📋 Employee Details")
                st.markdown(f"**Search Results for:** {st.session_state.get('searched_name', 'Unknown')}")
                
                # Display in a nice format
                st.markdown("---")
                st.text_area(
                    "Employee Information:",
                    st.session_state['employee_info'],
                    height=300,
                    disabled=True
                )
                
                # Download button for results
                st.download_button(
                    label="📥 Download Results",
                    data=st.session_state['employee_info'],
                    file_name=f"employee_info_{st.session_state.get('searched_name', 'unknown').replace(' ', '_')}.txt",
                    mime="text/plain"
                )
            
            # Display all employees if available
            if 'all_employees' in st.session_state:
                st.markdown("### 👥 All Employees Found")
                st.markdown("---")
                st.text_area(
                    "Complete Employee List:",
                    st.session_state['all_employees'],
                    height=200,
                    disabled=True
                )
        else:
            st.info("👆 Please upload a PDF file first to search for employees.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        <p>CGVAK SOFTWARE&EXPORTS - Employee Report Analyzer</p>
        <p>Powered by Streamlit + Ollama + PyPDF2</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()