import streamlit as st
import requests
import json
from typing import Optional
import time
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="SRI SAI AGENCIES - Premium Clothing",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .product-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2a5298;
    }
    .testimonial {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-style: italic;
    }
    .contact-info {
        background: #f1f8e9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .ai-chat {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffb74d;
    }
    .footer {
        background: #263238;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-top: 3rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def check_ollama_connection() -> tuple[bool, list]:
    """Check if Ollama is running and get available models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model['name'] for model in models_data.get('models', [])]
            return True, available_models
        return False, []
    except:
        return False, []

def get_ai_response(query: str, context: str = "", model: str = "mistral") -> Optional[str]:
    """Get response from Ollama Mistral model"""
    try:
        url = "http://localhost:11434/api/generate"
        
        prompt = f"""You are a helpful customer service representative for SRI SAI AGENCIES, a premium clothing company. 
        
        Company Context: {context}
        
        Customer Query: {query}
        
        Please provide a helpful, professional response about our clothing products, services, or company information. 
        Keep responses concise (under 200 words) and friendly. If asked about specific products, mention our quality and variety.
        
        Response:"""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 300
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Sorry, I could not process your request.')
        else:
            return "Sorry, our AI assistant is currently unavailable."
            
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Header Section
    st.markdown("""
    <div class="main-header">
        <h1>🏢 SRI SAI AGENCIES</h1>
        <h3>Premium Clothing & Fashion Solutions</h3>
        <p>Your Trusted Partner in Quality Apparel Since 1995</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.image("https://via.placeholder.com/200x100/2a5298/white?text=SRI+SAI+LOGO", width=200)
    st.sidebar.markdown("### 🧭 Navigation")
    
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["🏠 Home", "👔 Products", "🤖 AI Assistant", "📞 Contact", "ℹ️ About Us", "💬 Testimonials"]
    )
    
    # Check AI Assistant availability
    is_connected, available_models = check_ollama_connection()
    if is_connected:
        st.sidebar.success("🤖 AI Assistant: Online")
        suitable_models = [m for m in available_models if 'mistral' in m.lower()]
        ai_model = suitable_models[0] if suitable_models else (available_models[0] if available_models else "mistral")
    else:
        st.sidebar.error("🤖 AI Assistant: Offline")
        ai_model = "mistral"
    
    # Home Page
    if page == "🏠 Home":
        st.markdown("## Welcome to SRI SAI AGENCIES")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🌟 Why Choose SRI SAI AGENCIES?
            
            **Premium Quality Clothing** - We specialize in high-quality apparel for all occasions
            
            **🎯 Our Specialties:**
            - **Formal Wear**: Corporate suits, dress shirts, formal trousers
            - **Casual Wear**: T-shirts, jeans, casual shirts, polo shirts  
            - **Traditional Wear**: Kurtas, sarees, ethnic wear collections
            - **Kids Collection**: Comfortable and stylish children's clothing
            - **Accessories**: Ties, belts, scarves, and fashion accessories
            
            **✨ What Sets Us Apart:**
            - 25+ years of industry experience
            - Direct manufacturer relationships
            - Competitive wholesale and retail pricing
            - Custom tailoring services available
            - Quality assurance on all products
            """)
        
        with col2:
            st.markdown("""
            <div class="product-card">
                <h4>🎉 Current Offers</h4>
                <ul>
                    <li><strong>20% OFF</strong> on formal wear</li>
                    <li><strong>Buy 2 Get 1 FREE</strong> on casual shirts</li>
                    <li><strong>Special Discounts</strong> for bulk orders</li>
                    <li><strong>Free Alterations</strong> on suits</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="contact-info">
                <h4>📞 Quick Contact</h4>
                <p><strong>Phone:</strong> +91 98765 43210</p>
                <p><strong>Email:</strong> info@srisaiagencies.com</p>
                <p><strong>Timings:</strong> 9 AM - 8 PM</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Products Page
    elif page == "👔 Products":
        st.markdown("## 🛍️ Our Product Catalog")
        
        # Product categories
        category = st.selectbox(
            "Select Product Category:",
            ["All Products", "Formal Wear", "Casual Wear", "Traditional Wear", "Kids Collection", "Accessories"]
        )
        
        # Product showcase
        products = {
            "Formal Wear": [
                {"name": "Premium Business Suits", "price": "₹8,999 - ₹15,999", "desc": "Italian fabric, perfect fit"},
                {"name": "Formal Shirts", "price": "₹899 - ₹2,499", "desc": "Cotton blend, wrinkle-free"},
                {"name": "Dress Pants", "price": "₹1,299 - ₹3,999", "desc": "Comfortable formal trousers"},
                {"name": "Blazers", "price": "₹3,999 - ₹8,999", "desc": "Stylish blazers for every occasion"}
            ],
            "Casual Wear": [
                {"name": "Polo Shirts", "price": "₹599 - ₹1,299", "desc": "100% cotton, various colors"},
                {"name": "Casual Shirts", "price": "₹699 - ₹1,899", "desc": "Trendy patterns and designs"},
                {"name": "Jeans", "price": "₹1,199 - ₹2,999", "desc": "Premium denim, all sizes"},
                {"name": "T-Shirts", "price": "₹399 - ₹899", "desc": "Comfortable casual tees"}
            ],
            "Traditional Wear": [
                {"name": "Men's Kurtas", "price": "₹899 - ₹2,999", "desc": "Cotton and silk blend"},
                {"name": "Women's Sarees", "price": "₹1,999 - ₹9,999", "desc": "Designer and traditional sarees"},
                {"name": "Ethnic Sets", "price": "₹1,499 - ₹4,999", "desc": "Complete traditional outfits"},
                {"name": "Festive Collection", "price": "₹2,499 - ₹7,999", "desc": "Special occasion wear"}
            ],
            "Kids Collection": [
                {"name": "School Uniforms", "price": "₹499 - ₹1,299", "desc": "Durable and comfortable"},
                {"name": "Party Wear", "price": "₹899 - ₹2,499", "desc": "Stylish kids formal wear"},
                {"name": "Casual Sets", "price": "₹599 - ₹1,499", "desc": "Everyday comfort wear"},
                {"name": "Traditional Kids", "price": "₹799 - ₹1,999", "desc": "Ethnic wear for children"}
            ],
            "Accessories": [
                {"name": "Ties Collection", "price": "₹299 - ₹899", "desc": "Silk and polyester ties"},
                {"name": "Leather Belts", "price": "₹599 - ₹1,499", "desc": "Genuine leather, various styles"},
                {"name": "Scarves", "price": "₹399 - ₹1,199", "desc": "Designer scarves for all seasons"},
                {"name": "Pocket Squares", "price": "₹199 - ₹599", "desc": "Perfect formal accessories"}
            ]
        }
        
        if category == "All Products":
            for cat, items in products.items():
                st.markdown(f"### {cat}")
                cols = st.columns(2)
                for i, product in enumerate(items):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="product-card">
                            <h5>{product['name']}</h5>
                            <p><strong>Price:</strong> {product['price']}</p>
                            <p>{product['desc']}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            if category in products:
                st.markdown(f"### {category}")
                cols = st.columns(2)
                for i, product in enumerate(products[category]):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="product-card">
                            <h5>{product['name']}</h5>
                            <p><strong>Price:</strong> {product['price']}</p>
                            <p>{product['desc']}</p>
                            <button style="background-color: #2a5298; color: white; border: none; padding: 8px 16px; border-radius: 4px;">Inquire Now</button>
                        </div>
                        """, unsafe_allow_html=True)
    
    # AI Assistant Page
    elif page == "🤖 AI Assistant":
        st.markdown("## 🤖 Smart Shopping Assistant")
        
        if not is_connected:
            st.error("🚫 AI Assistant is currently offline. Please ensure Ollama is running with Mistral model.")
            st.markdown("""
            **To enable AI Assistant:**
            1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
            2. Start Ollama: `ollama serve`
            3. Pull Mistral: `ollama pull mistral`
            """)
        else:
            st.success(f"✅ AI Assistant is online using model: {ai_model}")
            
            st.markdown("""
            <div class="ai-chat">
                <h4>💬 Ask our AI Assistant</h4>
                <p>Get instant help with product information, sizing, recommendations, and more!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Chat interface
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            # Predefined quick questions
            st.markdown("### 🚀 Quick Questions:")
            quick_questions = [
                "What types of formal wear do you offer?",
                "Do you have custom tailoring services?",
                "What are your current offers and discounts?",
                "Can you help me choose the right size?",
                "Do you offer bulk order discounts?"
            ]
            
            cols = st.columns(2)
            for i, question in enumerate(quick_questions):
                with cols[i % 2]:
                    if st.button(question, key=f"quick_{i}"):
                        with st.spinner("Getting AI response..."):
                            context = "SRI SAI AGENCIES specializes in formal wear, casual wear, traditional wear, kids collection, and accessories. We offer custom tailoring, bulk discounts, and have 25+ years of experience."
                            response = get_ai_response(question, context, ai_model)
                            st.session_state.chat_history.append({"user": question, "ai": response, "time": datetime.now()})
            
            # Custom question input
            st.markdown("### ✍️ Ask Your Own Question:")
            user_question = st.text_input("Type your question here:", placeholder="e.g., What fabric options do you have for suits?")
            
            if st.button("🚀 Ask AI Assistant"):
                if user_question:
                    with st.spinner("AI is thinking..."):
                        context = "SRI SAI AGENCIES is a premium clothing company with 25+ years experience. We offer formal wear, casual wear, traditional wear, kids collection, and accessories. We provide custom tailoring, competitive pricing, and quality assurance."
                        response = get_ai_response(user_question, context, ai_model)
                        st.session_state.chat_history.append({"user": user_question, "ai": response, "time": datetime.now()})
                else:
                    st.warning("Please enter a question!")
            
            # Display chat history
            if st.session_state.chat_history:
                st.markdown("### 💬 Chat History:")
                for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 chats
                    st.markdown(f"**You:** {chat['user']}")
                    st.markdown(f"**AI Assistant:** {chat['ai']}")
                    st.markdown("---")
    
    # Contact Page
    elif page == "📞 Contact":
        st.markdown("## 📞 Contact SRI SAI AGENCIES")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="contact-info">
                <h4>🏢 Head Office</h4>
                <p><strong>Address:</strong><br>
                123, Fashion Street<br>
                Commercial Complex<br>
                Textile District<br>
                Chennai - 600001</p>
                
                <p><strong>📞 Phone:</strong> +91 98765 43210</p>
                <p><strong>📧 Email:</strong> info@srisaiagencies.com</p>
                <p><strong>🌐 Website:</strong> www.srisaiagencies.com</p>
                
                <h4>⏰ Business Hours</h4>
                <p><strong>Monday - Saturday:</strong> 9:00 AM - 8:00 PM</p>
                <p><strong>Sunday:</strong> 10:00 AM - 6:00 PM</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📝 Send us a Message")
            with st.form("contact_form"):
                name = st.text_input("Your Name *")
                email = st.text_input("Email Address *")
                phone = st.text_input("Phone Number")
                inquiry_type = st.selectbox("Inquiry Type", [
                    "General Inquiry", 
                    "Product Information", 
                    "Bulk Order", 
                    "Custom Tailoring", 
                    "Complaint/Feedback"
                ])
                message = st.text_area("Your Message *", height=100)
                
                submitted = st.form_submit_button("📧 Send Message")
                
                if submitted:
                    if name and email and message:
                        st.success("✅ Thank you! Your message has been sent. We'll get back to you within 24 hours.")
                    else:
                        st.error("❌ Please fill in all required fields marked with *")
    
    # About Us Page
    elif page == "ℹ️ About Us":
        st.markdown("## ℹ️ About SRI SAI AGENCIES")
        
        st.markdown("""
        ### 🏢 Our Story
        
        Founded in 1995, **SRI SAI AGENCIES** has been a trusted name in the clothing industry for over 25 years. 
        What started as a small family business has grown into one of the region's leading clothing retailers and wholesalers.
        
        ### 🎯 Our Mission
        To provide high-quality, affordable clothing solutions that meet the diverse needs of our customers while maintaining 
        the highest standards of service and customer satisfaction.

        ### 👥 Our Team
        Our experienced team of fashion experts, tailors, and customer service professionals work together to ensure 
        every customer finds exactly what they're looking for.

        ### 🏆 Our Achievements
        - **25+ Years** of industry experience
        - **10,000+** satisfied customers
        - **500+** product varieties
        - **50+** brand partnerships
        - **Multiple Awards** for customer service excellence
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 💼 Our Services
            - **Retail Sales** - Individual and family clothing needs
            - **Wholesale Trading** - Bulk orders for retailers
            - **Custom Tailoring** - Made-to-measure clothing
            - **Corporate Uniforms** - Office and industry uniforms
            - **Fashion Consulting** - Style and wardrobe advice
            """)
        
        with col2:
            st.markdown("""
            ### 🌟 Our Values
            - **Quality First** - Premium materials and craftsmanship
            - **Customer Focus** - Your satisfaction is our priority
            - **Fair Pricing** - Transparent and competitive rates
            - **Innovation** - Latest trends and technologies
            - **Integrity** - Honest and ethical business practices
            """)
    
    # Testimonials Page
    elif page == "💬 Testimonials":
        st.markdown("## 💬 What Our Customers Say")
        
        testimonials = [
            {
                "name": "Rajesh Kumar",
                "role": "Business Executive",
                "text": "Excellent quality formal wear! I've been buying suits from SRI SAI AGENCIES for 5 years. The fit is perfect and the fabric quality is outstanding.",
                "rating": "⭐⭐⭐⭐⭐"
            },
            {
                "name": "Priya Sharma",
                "role": "Fashion Enthusiast",
                "text": "Amazing collection of traditional wear! The sarees are beautiful and the customer service is exceptional. Highly recommended!",
                "rating": "⭐⭐⭐⭐⭐"
            },
            {
                "name": "Mohammed Ali",
                "role": "Retail Shop Owner",
                "text": "Best wholesale partner! Competitive prices, quality products, and timely delivery. They've helped grow my business significantly.",
                "rating": "⭐⭐⭐⭐⭐"
            },
            {
                "name": "Sunita Devi",
                "role": "Working Mother",
                "text": "Love their kids collection! My children's school uniforms and party wear are always from SRI SAI. Great quality and durability.",
                "rating": "⭐⭐⭐⭐⭐"
            },
            {
                "name": "Arjun Patel",
                "role": "College Student",
                "text": "Affordable casual wear with great variety. The staff helped me pick the perfect outfit for my placement interviews!",
                "rating": "⭐⭐⭐⭐⭐"
            },
            {
                "name": "Corporate HR Team",
                "role": "XYZ Company",
                "text": "Professional uniform service for our 200+ employees. Consistent quality, on-time delivery, and excellent customer support.",
                "rating": "⭐⭐⭐⭐⭐"
            }
        ]
        
        cols = st.columns(2)
        for i, testimonial in enumerate(testimonials):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="testimonial">
                    <p>"{testimonial['text']}"</p>
                    <p><strong>{testimonial['name']}</strong><br>
                    <em>{testimonial['role']}</em><br>
                    {testimonial['rating']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Add testimonial form
        st.markdown("### ✍️ Share Your Experience")
        with st.form("testimonial_form"):
            t_name = st.text_input("Your Name")
            t_role = st.text_input("Your Role/Profession")
            t_rating = st.selectbox("Rating", ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"])
            t_message = st.text_area("Your Experience", height=100)
            
            if st.form_submit_button("📝 Submit Testimonial"):
                if t_name and t_message:
                    st.success("✅ Thank you for your feedback! We appreciate your testimonial.")
                else:
                    st.error("❌ Please fill in your name and experience.")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <h3>🏢 SRI SAI AGENCIES</h3>
        <p>Your Trusted Partner in Premium Clothing</p>
        <p>📞 +91 98765 43210 | 📧 info@srisaiagencies.com</p>
        <p>© 2024 SRI SAI AGENCIES. All rights reserved.</p>
        <p>Powered by AI Technology & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()