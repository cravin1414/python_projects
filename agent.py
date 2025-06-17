import gradio as gr
import requests
import json
import time
from typing import Generator, Optional

class OllamaChat:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []
        self.refresh_models()
    
    def refresh_models(self) -> list:
        """Fetch available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['name'] for model in models_data.get('models', [])]
            else:
                self.available_models = []
        except requests.RequestException:
            self.available_models = []
        return self.available_models
    
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def stream_chat(self, model: str, messages: list, temperature: float = 0.7) -> Generator[str, None, None]:
        """Stream chat responses from Ollama"""
        if not model:
            yield "❌ Please select a model first."
            return
        
        if not self.check_ollama_status():
            yield "❌ Ollama is not running. Please start Ollama first."
            return
        
        try:
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature
                }
            }
            
            # Make streaming request
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                yield f"❌ Error: {response.status_code} - {response.text}"
                return
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if 'message' in chunk and 'content' in chunk['message']:
                            content = chunk['message']['content']
                            full_response += content
                            yield full_response
                        
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except requests.RequestException as e:
            yield f"❌ Connection error: {str(e)}"
        except Exception as e:
            yield f"❌ Unexpected error: {str(e)}"

# Initialize Ollama client
ollama_client = OllamaChat()

def format_chat_history(history):
    """Convert Gradio chat history to Ollama message format"""
    messages = []
    for user_msg, assistant_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})
    return messages

def chat_with_ollama(message, history, model, temperature, max_tokens):
    """Handle chat interaction with Ollama"""
    if not message.strip():
        return history, ""
    
    # Add user message to history
    history.append([message, ""])
    
    # Convert history to Ollama format
    messages = format_chat_history(history[:-1])  # Exclude the last empty assistant message
    messages.append({"role": "user", "content": message})
    
    # Stream the response
    for partial_response in ollama_client.stream_chat(model, messages, temperature):
        history[-1][1] = partial_response
        yield history, ""
    
    return history, ""

def refresh_models():
    """Refresh the list of available models"""
    models = ollama_client.refresh_models()
    if models:
        return gr.update(choices=models, value=models[0] if models else None)
    else:
        return gr.update(choices=[], value=None)

def check_status():
    """Check Ollama connection status"""
    if ollama_client.check_ollama_status():
        models = ollama_client.refresh_models()
        if models:
            return f"✅ Connected to Ollama | Available models: {len(models)}"
        else:
            return "⚠️ Connected to Ollama but no models found"
    else:
        return "❌ Cannot connect to Ollama. Make sure it's running on http://localhost:11434"

# Create Gradio interface
with gr.Blocks(title="Ollama Chat Interface", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🦙 Ollama Chat Interface")
    gr.Markdown("Chat with your local Ollama models without any API calls!")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Status section
            status_display = gr.Textbox(
                label="Connection Status",
                value=check_status(),
                interactive=False,
                max_lines=2
            )
            
            refresh_btn = gr.Button("🔄 Refresh Models", variant="secondary")
            
            # Model selection
            model_dropdown = gr.Dropdown(
                label="Select Model",
                choices=ollama_client.available_models,
                value=ollama_client.available_models[0] if ollama_client.available_models else None,
                interactive=True
            )
            
            # Parameters
            temperature_slider = gr.Slider(
                label="Temperature",
                minimum=0.0,
                maximum=2.0,
                value=0.7,
                step=0.1,
                info="Controls randomness in responses"
            )
            
            max_tokens_slider = gr.Slider(
                label="Max Tokens",
                minimum=50,
                maximum=4000,
                value=1000,
                step=50,
                info="Maximum length of response"
            )
            
            # Instructions
            gr.Markdown("""
            ### 📝 Instructions:
            1. **Start Ollama**: Run `ollama serve` in terminal
            2. **Install Models**: Run `ollama pull <model-name>` (e.g., `ollama pull llama2`)
            3. **Refresh**: Click refresh button to load models
            4. **Chat**: Select a model and start chatting!
            
            ### 🔧 Troubleshooting:
            - If no models appear, run `ollama list` to check installed models
            - Make sure Ollama is running on port 11434
            - Try `ollama pull llama2` to install a basic model
            """)
        
        with gr.Column(scale=2):
            # Chat interface
            chatbot = gr.Chatbot(
                label="Chat",
                height=500,
                show_copy_button=True,
                bubble_full_width=False
            )
            
            msg_input = gr.Textbox(
                label="Message",
                placeholder="Type your message here...",
                lines=2,
                max_lines=5
            )
            
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear Chat", variant="secondary")
    
    # Event handlers
    def clear_chat():
        return [], ""
    
    def update_status():
        return check_status()
    
    # Refresh models and update status
    refresh_btn.click(
        fn=lambda: [refresh_models(), update_status()],
        outputs=[model_dropdown, status_display]
    )
    
    # Send message
    msg_input.submit(
        fn=chat_with_ollama,
        inputs=[msg_input, chatbot, model_dropdown, temperature_slider, max_tokens_slider],
        outputs=[chatbot, msg_input]
    )
    
    send_btn.click(
        fn=chat_with_ollama,
        inputs=[msg_input, chatbot, model_dropdown, temperature_slider, max_tokens_slider],
        outputs=[chatbot, msg_input]
    )
    
    # Clear chat
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, msg_input]
    )
    
    # Auto-refresh status on load
    app.load(
        fn=update_status,
        outputs=status_display
    )

if __name__ == "__main__":
    print("🚀 Starting Ollama Chat Interface...")
    print("📋 Make sure Ollama is running: ollama serve")
    print("📦 Install models with: ollama pull <model-name>")
    print("🌐 Interface will be available at: http://localhost:7860")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )