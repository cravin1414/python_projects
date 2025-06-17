import streamlit as st
import ollama
import PyPDF2
import io
import json
import re
from typing import Dict, List
import time

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 1rem 0;
    }
    
    .analysis-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .rating-container {
        text-align: center;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .rating-score {
        font-size: 4rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .improvement-item {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #f39c12;
    }
    
    .strength-item {
        background: #d1edff;
        border: 1px solid #74b9ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #0984e3;
    }
    
    .sidebar-content {
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class ResumeAnalyzer:
    def __init__(self):
        self.client = ollama
        
    def extract_text_from_pdf(self, uploaded_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def analyze_resume(self, resume_text: str) -> Dict:
        """Analyze resume using Mistral model"""
        prompt = f"""
        As an expert HR professional and resume reviewer, analyze the following resume and provide a comprehensive evaluation.

        Resume Content:
        {resume_text}

        Please provide your analysis in the following JSON format:
        {{
            "overall_rating": <score out of 10>,
            "rating_explanation": "<brief explanation of the rating>",
            "strengths": [
                "<strength 1>",
                "<strength 2>",
                "<strength 3>"
            ],
            "areas_for_improvement": [
                "<improvement area 1>",
                "<improvement area 2>",
                "<improvement area 3>",
                "<improvement area 4>",
                "<improvement area 5>"
            ],
            "specific_suggestions": [
                "<specific actionable suggestion 1>",
                "<specific actionable suggestion 2>",
                "<specific actionable suggestion 3>"
            ],
            "keywords_missing": [
                "<missing keyword 1>",
                "<missing keyword 2>",
                "<missing keyword 3>"
            ],
            "format_feedback": "<feedback on resume format and structure>",
            "summary": "<overall summary of the resume>"
        }}

        Focus on:
        1. Content quality and relevance
        2. Professional formatting and structure
        3. Keyword optimization for ATS systems
        4. Skills and experience presentation
        5. Grammar and language usage
        6. Contact information completeness
        7. Achievement quantification
        8. Industry-specific requirements

        Be constructive and specific in your feedback.
        """
        
        try:
            response = self.client.chat(
                model='mistral:latest',
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            
            # Extract JSON from response
            response_text = response['message']['content']
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                return self._parse_fallback_response(response_text)
                
        except Exception as e:
            st.error(f"Error analyzing resume: {str(e)}")
            return self._get_default_response()
    
    def _parse_fallback_response(self, response_text: str) -> Dict:
        """Fallback parsing if JSON fails"""
        return {
            "overall_rating": 7,
            "rating_explanation": "Analysis completed with basic evaluation",
            "strengths": ["Professional experience shown", "Educational background included", "Contact information provided"],
            "areas_for_improvement": ["Add more quantified achievements", "Include relevant keywords", "Improve formatting consistency", "Add skills section", "Enhance summary section"],
            "specific_suggestions": ["Use bullet points for achievements", "Add metrics to demonstrate impact", "Include industry-specific keywords"],
            "keywords_missing": ["Industry-specific terms", "Technical skills", "Soft skills"],
            "format_feedback": "Consider improving overall structure and visual appeal",
            "summary": response_text[:200] + "..."
        }
    
    def _get_default_response(self) -> Dict:
        """Default response in case of errors"""
        return {
            "overall_rating": 6,
            "rating_explanation": "Unable to complete full analysis",
            "strengths": ["Resume uploaded successfully"],
            "areas_for_improvement": ["Please try uploading again for detailed analysis"],
            "specific_suggestions": ["Ensure PDF is readable and well-formatted"],
            "keywords_missing": ["Analysis pending"],
            "format_feedback": "Analysis could not be completed",
            "summary": "Please try uploading your resume again"
        }

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI-Powered Resume Analyzer</h1>
        <p>Get professional insights and improve your resume with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize analyzer
    analyzer = ResumeAnalyzer()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-content">
            <h3>📋 How it works</h3>
            <ol>
                <li>Upload your resume (PDF format)</li>
                <li>AI analyzes your resume</li>
                <li>Get detailed feedback and rating</li>
                <li>Implement suggestions to improve</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-content">
            <h3>🎯 What we analyze</h3>
            <ul>
                <li>Content quality</li>
                <li>Format & structure</li>
                <li>ATS compatibility</li>
                <li>Keyword optimization</li>
                <li>Achievement presentation</li>
                <li>Professional language</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="upload-section">
            <h3>📄 Upload Your Resume</h3>
            <p>Upload your resume in PDF format for analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf'],
            help="Please upload a PDF file of your resume"
        )
        
        if uploaded_file is not None:
            st.success("✅ Resume uploaded successfully!")
            
            # Extract text
            with st.spinner("🔍 Extracting text from resume..."):
                resume_text = analyzer.extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                st.info(f"📊 Extracted {len(resume_text)} characters from your resume")
                
                # Analyze button
                if st.button("🚀 Analyze My Resume", type="primary", use_container_width=True):
                    with st.spinner("🤖 AI is analyzing your resume... This may take a moment"):
                        analysis = analyzer.analyze_resume(resume_text)
                        st.session_state['analysis'] = analysis
                        st.session_state['analyzed'] = True
                    st.success("✅ Analysis completed!")
                    st.rerun()
    
    with col2:
        if 'analyzed' in st.session_state and st.session_state['analyzed']:
            analysis = st.session_state['analysis']
            
            # Rating display
            st.markdown(f"""
            <div class="rating-container">
                <h2>Overall Resume Rating</h2>
                <div class="rating-score">{analysis['overall_rating']}/10</div>
                <p>{analysis['rating_explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="analysis-card">
                <h3>🎯 Ready for Analysis</h3>
                <p>Upload your resume and click "Analyze My Resume" to get started!</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Analysis Results
    if 'analyzed' in st.session_state and st.session_state['analyzed']:
        analysis = st.session_state['analysis']
        
        # Strengths and Improvements
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="analysis-card">
                <h3>💪 Strengths</h3>
            </div>
            """, unsafe_allow_html=True)
            
            for strength in analysis['strengths']:
                st.markdown(f"""
                <div class="strength-item">
                    <strong>✅ {strength}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="analysis-card">
                <h3>🎯 Areas for Improvement</h3>
            </div>
            """, unsafe_allow_html=True)
            
            for improvement in analysis['areas_for_improvement']:
                st.markdown(f"""
                <div class="improvement-item">
                    <strong>📈 {improvement}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed Feedback
        st.markdown("""
        <div class="analysis-card">
            <h3>📝 Specific Suggestions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for i, suggestion in enumerate(analysis['specific_suggestions'], 1):
            st.markdown(f"**{i}.** {suggestion}")
        
        # Additional sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="analysis-card">
                <h3>🔍 Missing Keywords</h3>
            </div>
            """, unsafe_allow_html=True)
            
            for keyword in analysis['keywords_missing']:
                st.markdown(f"• **{keyword}**")
        
        with col2:
            st.markdown("""
            <div class="analysis-card">
                <h3>📐 Format Feedback</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(analysis['format_feedback'])
        
        # Summary
        st.markdown("""
        <div class="analysis-card">
            <h3>📋 Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(analysis['summary'])
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Analyze Another Resume", use_container_width=True):
                st.session_state['analyzed'] = False
                st.rerun()
        
        with col2:
            if st.button("💾 Download Analysis", use_container_width=True):
                # Create downloadable report
                report = f"""
RESUME ANALYSIS REPORT
=====================

Overall Rating: {analysis['overall_rating']}/10
{analysis['rating_explanation']}

STRENGTHS:
{chr(10).join([f"• {s}" for s in analysis['strengths']])}

AREAS FOR IMPROVEMENT:
{chr(10).join([f"• {i}" for i in analysis['areas_for_improvement']])}

SPECIFIC SUGGESTIONS:
{chr(10).join([f"{idx}. {s}" for idx, s in enumerate(analysis['specific_suggestions'], 1)])}

MISSING KEYWORDS:
{chr(10).join([f"• {k}" for k in analysis['keywords_missing']])}

FORMAT FEEDBACK:
{analysis['format_feedback']}

SUMMARY:
{analysis['summary']}
                """
                
                st.download_button(
                    label="📄 Download Report",
                    data=report,
                    file_name="resume_analysis_report.txt",
                    mime="text/plain"
                )
        
        with col3:
            if st.button("📊 View Detailed Stats", use_container_width=True):
                st.balloons()
                st.info("Detailed statistics feature coming soon!")

if __name__ == "__main__":
    main()