import streamlit as st
import PyPDF2
import requests
import json
import io
import time
from typing import Optional
import re

# Configure Streamlit page
st.set_page_config(
    page_title="Medical Report Analyzer",
    page_icon="🏥",
    layout="wide"
)

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file using PyPDF2"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text.strip():  # Only add non-empty pages
                text += page_text + "\n"
        
        # Clean up the text
        text = re.sub(r'\n+', '\n', text)  # Remove multiple newlines
        text = re.sub(r'\s+', ' ', text)   # Remove extra spaces
        
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def chunk_text(text: str, max_words: int = 800) -> list:
    """Split text into smaller chunks to avoid timeout"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_words):
        chunk = ' '.join(words[i:i + max_words])
        chunks.append(chunk)
    
    return chunks

def analyze_with_ollama_streaming(text: str, model: str = "mistral") -> Optional[str]:
    """Send text to Ollama for analysis using streaming to avoid timeout"""
    try:
        url = "http://localhost:11434/api/generate"
        
        # Create optimized analysis prompt
        prompt = f"""Analyze this medical report concisely. Provide:

**KEY FINDINGS:** (2-3 main points)
**CONDITIONS:** (list medical conditions found)
**MEDICATIONS:** (list any medications mentioned)
**RECOMMENDATIONS:** (important follow-up actions)
**CRITICAL ALERTS:** (urgent items requiring attention)

Medical Text:
{text[:3000]}...

Keep response under 500 words and be specific:"""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,  # Use streaming to avoid timeout
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 800  # Limit response length
            }
        }
        
        response = requests.post(url, json=payload, stream=True, timeout=300)
        
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line)
                        if 'response' in json_response:
                            full_response += json_response['response']
                        if json_response.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
            
            return full_response if full_response else "No response generated"
        else:
            st.error(f"Ollama API error: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out even with streaming. Try with shorter text.")
        return None
    except Exception as e:
        st.error(f"Error calling Ollama: {str(e)}")
        return None

def analyze_with_ollama_batch(text: str, model: str = "mistral") -> Optional[str]:
    """Analyze text in smaller batches if it's too long"""
    try:
        # If text is too long, split into chunks
        if len(text.split()) > 1000:
            chunks = chunk_text(text, 600)  # Smaller chunks
            analyses = []
            
            progress_bar = st.progress(0)
            
            for i, chunk in enumerate(chunks):
                st.info(f"Processing chunk {i+1}/{len(chunks)}...")
                
                analysis = analyze_with_ollama_streaming(chunk, model)
                if analysis:
                    analyses.append(f"**Section {i+1}:**\n{analysis}\n")
                
                progress_bar.progress((i + 1) / len(chunks))
                time.sleep(1)  # Brief pause between requests
            
            # Combine all analyses
            if analyses:
                combined = "\n".join(analyses)
                
                # Create final summary
                summary_prompt = f"""Summarize these medical report analyses into one cohesive report:

{combined[:2000]}

Provide final consolidated:
**OVERALL SUMMARY:**
**ALL CONDITIONS FOUND:**
**ALL MEDICATIONS:**
**PRIORITY RECOMMENDATIONS:**
**CRITICAL ITEMS:**"""
                
                final_analysis = analyze_with_ollama_streaming(summary_prompt, model)
                return final_analysis if final_analysis else "\n".join(analyses)
            else:
                return "Failed to analyze any sections"
        else:
            # Text is short enough, analyze directly
            return analyze_with_ollama_streaming(text, model)
    
    except Exception as e:
        st.error(f"Batch analysis error: {str(e)}")
        return None

def check_ollama_connection() -> tuple[bool, list]:
    """Check if Ollama is running and get available models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            return True, available_models
        return False, []
    except:
        return False, []

def test_model_response(model: str) -> bool:
    """Test if the selected model responds properly"""
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": "Say 'Model is working'",
            "stream": False,
            "options": {"num_predict": 10}
        }
        
        response = requests.post(url, json=payload, timeout=30)
        return response.status_code == 200
    except:
        return False

def main():
    st.title("🏥 Enhanced Medical Report Analyzer")
    st.markdown("Upload a PDF medical report for AI-powered analysis using Ollama")
    
    # Check Ollama connection and get available models
    is_connected, available_models = check_ollama_connection()
    
    if not is_connected:
        st.error("⚠️ Cannot connect to Ollama. Please ensure:")
        st.markdown("""
        1. **Install Ollama**: `curl -fsSL https://ollama.ai/install.sh | sh`
        2. **Start Ollama**: `ollama serve`
        3. **Pull a model**: `ollama pull mistral` or `ollama pull llama2`
        """)
        st.stop()
    
    st.success("✅ Connected to Ollama successfully")
    
    # Model selection with available models
    st.sidebar.header("🔧 Configuration")
    
    if available_models:
        # Filter for medical-suitable models
        preferred_models = [m for m in available_models if any(name in m.lower() for name in ['mistral', 'llama', 'codellama', 'dolphin'])]
        model_options = preferred_models if preferred_models else available_models
        
        model_name = st.sidebar.selectbox(
            "Select Model",
            model_options,
            help="Choose an available Ollama model"
        )
        
        # Test model
        if st.sidebar.button("🧪 Test Model"):
            with st.spinner("Testing model..."):
                if test_model_response(model_name):
                    st.sidebar.success(f"✅ {model_name} is working!")
                else:
                    st.sidebar.error(f"❌ {model_name} failed to respond")
    else:
        st.error("No models found. Please pull a model: `ollama pull mistral`")
        st.stop()
    
    # Advanced options
    with st.sidebar.expander("⚙️ Advanced Options"):
        max_chunk_words = st.slider("Max words per chunk", 300, 1000, 600)
        use_batch_processing = st.checkbox("Use batch processing for long texts", True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "📤 Choose a PDF medical report",
        type="pdf",
        help="Upload a PDF file containing the medical report"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Create columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Extracted Text")
            
            # Extract text from PDF
            with st.spinner("Extracting text from PDF..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
            
            if extracted_text:
                # Show preview
                preview_text = extracted_text[:2000] + "..." if len(extracted_text) > 2000 else extracted_text
                st.text_area(
                    "Text Preview",
                    value=preview_text,
                    height=300,
                    disabled=True
                )
                
                # Statistics
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                st.info(f"📊 Statistics: {word_count} words, {char_count} characters")
                
                if word_count > 1000:
                    st.warning(f"⚠️ Large document detected. Will use batch processing.")
                
            else:
                st.error("❌ Could not extract text from PDF")
                st.stop()
        
        with col2:
            st.subheader("🤖 AI Analysis")
            
            if st.button("🔍 Analyze Medical Report", type="primary"):
                if extracted_text:
                    start_time = time.time()
                    
                    with st.spinner(f"Analyzing with {model_name}... Please wait."):
                        if use_batch_processing and len(extracted_text.split()) > 800:
                            analysis = analyze_with_ollama_batch(extracted_text, model_name)
                        else:
                            analysis = analyze_with_ollama_streaming(extracted_text, model_name)
                    
                    end_time = time.time()
                    processing_time = round(end_time - start_time, 2)
                    
                    if analysis:
                        st.success(f"✅ Analysis completed in {processing_time} seconds")
                        st.markdown("### 📋 Analysis Results")
                        st.markdown(analysis)
                        
                        # Download options
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.download_button(
                                "💾 Download Analysis",
                                data=analysis,
                                file_name=f"analysis_{uploaded_file.name}.txt",
                                mime="text/plain"
                            )
                        with col_b:
                            st.download_button(
                                "📄 Download Full Report",
                                data=f"ORIGINAL TEXT:\n{extracted_text}\n\n{'='*50}\n\nANALYSIS:\n{analysis}",
                                file_name=f"full_report_{uploaded_file.name}.txt",
                                mime="text/plain"
                            )
                    else:
                        st.error("❌ Analysis failed. Try with a different model or shorter text.")
                else:
                    st.error("❌ No text to analyze")
    
    # Instructions
    with st.expander("ℹ️ Usage Instructions"):
        st.markdown("""
        ### Quick Setup (if you haven't installed Ollama):
        ```bash
        # Install Ollama
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Start Ollama service
        ollama serve
        
        # Pull a model (in another terminal)
        ollama pull mistral
        ```
        
        ### Features:
        - ✅ **Smart chunking** for large documents
        - ✅ **Streaming responses** to prevent timeouts  
        - ✅ **Batch processing** for comprehensive analysis
        - ✅ **Model testing** to verify functionality
        - ✅ **Progress tracking** for long documents
        - ✅ **Download options** for results
        
        ### Troubleshooting:
        - **Timeout issues**: Use batch processing for large files
        - **Model not responding**: Test the model first
        - **Connection failed**: Ensure Ollama is running (`ollama serve`)
        """)
    
    st.markdown("---")
    st.markdown("⚠️ **Disclaimer**: This tool is for informational purposes only. Always consult healthcare professionals for medical decisions.")

if __name__ == "__main__":
    main()