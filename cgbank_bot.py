import json
import re
import random
from datetime import datetime, timedelta
import hashlib
import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, List, Optional, Union, Any
import ollama
from difflib import get_close_matches

# Load the bank data
with open('cgbank_data.json', 'r') as f:
    BANK_DATA = json.load(f)

class CGBankDatabase:
    """Class to interact with the bank data"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = "CGBank_Salt_Value_123!"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @staticmethod
    def get_user(username: str) -> Optional[Dict[str, Any]]:
        """Get user data by username (case-insensitive)"""
        username_lower = username.lower()
        for uname, user_data in BANK_DATA['users'].items():
            if uname.lower() == username_lower:
                return user_data
        return None
    
    @staticmethod
    def verify_user(username: str, password: str) -> bool:
        """Verify user credentials"""
        user = CGBankDatabase.get_user(username)
        if not user:
            return False
        # Compare hashed passwords
        return user['password'] == password  # Note: Storing plaintext passwords is insecure - this is just for demo
    
    @staticmethod
    def get_bank_info() -> Dict[str, Any]:
        """Get bank information"""
        return BANK_DATA['bank_info']
    
    @staticmethod
    def get_loan_products() -> Dict[str, Any]:
        """Get loan products information"""
        return BANK_DATA['loan_products']
    
    @staticmethod
    def get_government_schemes() -> Dict[str, Any]:
        """Get government schemes information"""
        return BANK_DATA['government_schemes']
    
    @staticmethod
    def get_user_transactions(username: str) -> List[Dict[str, Any]]:
        """Get transaction history for a user"""
        user = CGBankDatabase.get_user(username)
        if not user:
            return []
        
        # Use the predefined transactions from the JSON data
        transactions = []
        for txn in BANK_DATA['transactions_history']:
            transaction = {
                'date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'description': txn['name'],
                'amount': txn['amt'],
                'balance': user['balance'] - random.uniform(0, 1000)  # Random balance for demo
            }
            transactions.append(transaction)
        
        return sorted(transactions, key=lambda x: x['date'], reverse=True)
    
    @staticmethod
    def get_user_bills(username: str) -> List[Dict[str, Any]]:
        """Get bills for a user"""
        return BANK_DATA['bills']
    
    @staticmethod
    def get_spending_categories(username: str) -> List[Dict[str, Any]]:
        """Get spending categories for a user"""
        return BANK_DATA['spending_categories']

class RexaBot:
    """CGBank's intelligent banking assistant with enhanced NLP capabilities"""
    
    def __init__(self):
        self.name = "Rexa"
        self.service_keywords = {
            'balance_inquiry': ['balance', 'account balance', 'how much money', 'check balance', 
                              'current balance', 'what do i have', 'funds available', 'available balance',
                              'remaining balance', 'account summary'],
            'transaction_history': ['transaction', 'history', 'statement', 'recent transactions', 
                                  'last transactions', 'past payments', 'my spending', 'past expenses',
                                  'payment history', 'account statement'],
            'fund_transfer': ['transfer', 'send money', 'transfer money', 'transfer funds', 
                            'move money', 'pay someone', 'send to friend', 'wire transfer',
                            'remit', 'send cash'],
            'bill_payment': ['pay bill', 'bill payment', 'utility bill', 'electricity bill', 
                           'water bill', 'gas bill', 'phone bill', 'internet bill',
                           'credit card bill', 'mobile recharge'],
            'bank_info': ['about cgbank', 'bank information', 'bank details', 'what is cgbank', 
                         'bank services', 'products offered', 'bank features', 'branch locations',
                         'contact bank', 'bank timings'],
            'loan_info': ['loan', 'borrow', 'credit', 'home loan', 'personal loan', 'car loan',
                         'education loan', 'interest rates', 'eligibility', 'how to apply',
                         'mortgage', 'vehicle loan', 'student loan'],
            'scheme_info': ['modi scheme', 'pm farmer scheme', 'thangamagal scheme', 'government scheme',
                          'scheme details', 'scheme information', 'subsidy', 'farmer benefits',
                          'women benefits', 'agricultural scheme']
        }
        
        # Create a knowledge base from the JSON data
        self.knowledge_base = self._create_knowledge_base()
    
    def _create_knowledge_base(self) -> Dict[str, Any]:
        """Create a structured knowledge base from the JSON data"""
        kb = {
            'bank': BANK_DATA['bank_info'],
            'loans': BANK_DATA['loan_products'],
            'schemes': BANK_DATA['government_schemes'],
            'services': BANK_DATA['bank_info']['services'],
            'branches': BANK_DATA['bank_info']['branches']
        }
        return kb
    
    def _get_random_response(self, response_type: str) -> str:
        """Get a random response of a given type"""
        return random.choice(BANK_DATA['bot_responses'].get(response_type, ["I'm here to help."]))
    
    def _extract_loan_info(self, loan_type: str) -> str:
        """Enhanced loan info extraction with fuzzy matching"""
        loans = CGBankDatabase.get_loan_products()
        
        # Try exact match first
        for key, loan_data in loans.items():
            if loan_type.lower() in loan_data['name'].lower():
                return self._format_loan_response(loan_data)
        
        # Try fuzzy matching if exact match not found
        loan_names = [loan['name'].lower() for loan in loans.values()]
        matches = get_close_matches(loan_type.lower(), loan_names, n=1, cutoff=0.6)
        
        if matches:
            matched_loan_name = matches[0]
            for loan_data in loans.values():
                if loan_data['name'].lower() == matched_loan_name:
                    return self._format_loan_response(loan_data)
        
        # If no match found, return all loans
        return self._get_all_loans_info()
    
    def _format_loan_response(self, loan_data: Dict[str, Any]) -> str:
        """Format loan information into a response"""
        return (f"**{loan_data['name']}**\n"
               f"- Amount: {loan_data['amount']}\n"
               f"- Interest Rate: {loan_data['interest']}\n"
               f"- Tenure: {loan_data['tenure']}\n\n"
               f"Visit any CGBank branch to apply!")
    
    def _get_all_loans_info(self) -> str:
        """Get information about all loan products"""
        loans = CGBankDatabase.get_loan_products()
        response = "**Loan Products at CGBank:**\n\n"
        for loan in loans.values():
            response += (f"**{loan['name']}**\n"
                        f"- Amount: {loan['amount']}\n"
                        f"- Interest: {loan['interest']}\n"
                        f"- Tenure: {loan['tenure']}\n\n")
        return response
    
    def _extract_scheme_info(self, scheme_name: str) -> str:
        """Enhanced scheme info extraction with fuzzy matching"""
        schemes = CGBankDatabase.get_government_schemes()
        
        # Try exact match first
        for key, scheme_data in schemes.items():
            if scheme_name.lower() in scheme_data['name'].lower():
                return self._format_scheme_response(scheme_data)
        
        # Try fuzzy matching if exact match not found
        scheme_names = [scheme['name'].lower() for scheme in schemes.values()]
        matches = get_close_matches(scheme_name.lower(), scheme_names, n=1, cutoff=0.6)
        
        if matches:
            matched_scheme_name = matches[0]
            for scheme_data in schemes.values():
                if scheme_data['name'].lower() == matched_scheme_name:
                    return self._format_scheme_response(scheme_data)
        
        # If no match found, return all schemes
        return self._get_all_schemes_info()
    
    def _format_scheme_response(self, scheme_data: Dict[str, Any]) -> str:
        """Format scheme information into a response"""
        benefits = "\n".join([f"- {benefit}" for benefit in scheme_data['benefits']])
        return (f"**{scheme_data['name']}**\n\n"
               f"**Benefits:**\n{benefits}\n\n"
               f"**Eligibility:** {scheme_data['eligibility']}\n\n"
               f"**How to Apply:** {scheme_data['application']}")
    
    def _get_all_schemes_info(self) -> str:
        """Get information about all government schemes"""
        schemes = CGBankDatabase.get_government_schemes()
        response = "**Government Schemes at CGBank:**\n\n"
        for scheme in schemes.values():
            response += f"**{scheme['name']}**\n"
            response += f"- Eligibility: {scheme['eligibility']}\n\n"
        return response
    
    def _get_ollama_response(self, message: str, context: str = "") -> str:
        """Get a response from Ollama LLM with banking context"""
        try:
            # Prepare the prompt with context
            prompt = f"""
            You are Rexa, an AI banking assistant for CGBank. Provide helpful, accurate responses 
            to customer queries about banking services. Use the following context when relevant:
            
            {context}
            
            Knowledge Base:
            {json.dumps(self.knowledge_base, indent=2)}
            
            Customer Query: {message}
            
            Guidelines:
            1. Be polite and professional
            2. Provide accurate information from the knowledge base
            3. If unsure, ask for clarification
            4. Keep responses concise but helpful
            5. For account-specific queries, verify user is logged in
            
            Response:
            """
            
            # Call Ollama API
            response = ollama.generate(
                model='banking-assistant',  # Use an appropriate model
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'max_tokens': 200,
                    'top_p': 0.9
                }
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Error getting Ollama response: {e}")
            return "I'm having trouble processing your request. Please try again later."
    
    def _identify_intent(self, message: str) -> Optional[str]:
        """Identify the intent of the user message using NLP techniques"""
        message = message.lower()
        
        # Check for exact matches first
        for intent, keywords in self.service_keywords.items():
            if any(re.search(r'\b' + re.escape(keyword) + r'\b', message) for keyword in keywords):
                return intent
        
        # Check for similar phrases using fuzzy matching
        all_keywords = [kw for sublist in self.service_keywords.values() for kw in sublist]
        matches = get_close_matches(message, all_keywords, n=1, cutoff=0.6)
        
        if matches:
            matched_keyword = matches[0]
            for intent, keywords in self.service_keywords.items():
                if matched_keyword in keywords:
                    return intent
        
        return None
    
    def process_message(self, message: str, username: Optional[str] = None) -> str:
        """Process a user message with enhanced NLP and return an appropriate response"""
        message = message.lower()
        user_data = CGBankDatabase.get_user(username) if username else None
        
        # Identify intent using NLP
        intent = self._identify_intent(message)
        
        # Handle greetings
        if any(word in message for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            if user_data:
                return f"Hello {user_data['name']}! {self._get_random_response('greetings')}"
            return self._get_random_response('greetings')
        
        # Handle thanks
        if any(word in message for word in ['thank', 'thanks', 'appreciate']):
            return self._get_random_response('thanks')
        
        # Handle identified intents
        if intent == 'balance_inquiry':
            if user_data:
                return self._get_random_response('balance_inquiry').format(balance=user_data['balance'])
            return "Please log in to check your account balance."
        
        elif intent == 'transaction_history':
            if user_data:
                transactions = CGBankDatabase.get_user_transactions(username)[:5]
                response = "Here are your recent transactions:\n\n"
                for i, txn in enumerate(transactions, 1):
                    sign = "+" if txn['amount'] > 0 else ""
                    response += (f"{i}. {txn['description']}\n"
                                f"   Amount: {sign}₹{txn['amount']:,.2f}\n"
                                f"   Date: {txn['date'].strftime('%Y-%m-%d')}\n"
                                f"   Balance: ₹{txn['balance']:,.2f}\n\n")
                return response
            return "Please log in to view your transaction history."
        
        elif intent == 'fund_transfer':
            if user_data:
                return self._get_random_response('fund_transfer')
            return "Please log in to initiate a fund transfer."
        
        elif intent == 'bill_payment':
            if user_data:
                return self._get_random_response('bill_payment')
            return "Please log in to pay your bills."
        
        elif intent == 'bank_info':
            bank_info = CGBankDatabase.get_bank_info()
            if 'branch' in message or 'location' in message:
                branches = "\n".join([f"- {branch['name']}: {branch['address']}" 
                                    for branch in bank_info['branches']])
                return f"**CGBank Branches:**\n{branches}"
            elif 'service' in message or 'product' in message:
                services = "\n".join([f"- {service}" for service in bank_info['services']])
                return f"**CGBank Services:**\n{services}"
            elif 'time' in message or 'hour' in message:
                timings = bank_info['branches'][0]['timings']
                return f"**Branch Timings:**\n{timings}"
            else:
                return (f"**About {bank_info['name']}:**\n"
                       f"{bank_info['tagline']}\n\n"
                       f"**Address:** {bank_info['address']}\n"
                       f"**Contact:** {bank_info['contact']}\n"
                       f"**Email:** {bank_info['email']}\n"
                       f"**Helpline:** {bank_info['helpline']}")
        
        elif intent == 'loan_info':
            if 'personal' in message:
                return self._extract_loan_info('Personal Loan')
            elif 'home' in message:
                return self._extract_loan_info('Home Loan')
            elif 'car' in message or 'auto' in message:
                return self._extract_loan_info('Car Loan')
            elif 'education' in message:
                return self._extract_loan_info('Education Loan')
            else:
                return self._get_all_loans_info()
        
        elif intent == 'scheme_info':
            if 'modi' in message:
                return self._extract_scheme_info('Modi Scheme')
            elif 'farmer' in message:
                return self._extract_scheme_info('PM Farmer Scheme')
            elif 'thangamagal' in message or 'women' in message:
                return self._extract_scheme_info('Thangamagal Scheme')
            else:
                return self._get_all_schemes_info()
        
        context = ""
        if user_data:
            context = f"Customer: {user_data['name']}, Account Balance: ₹{user_data['balance']:,.2f}"
        
        return self._get_ollama_response(message, context)

class CGBankApp:
    """Streamlit application for CGBank"""
    
    def __init__(self):
        self.bot = RexaBot()
        self._initialize_session_state()
        self._setup_page_config()
        self._load_custom_styles()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'page' not in st.session_state:
            st.session_state.page = "login"
        if 'bot_conversation' not in st.session_state:
            st.session_state.bot_conversation = []
        if 'show_popup_bot' not in st.session_state:
            st.session_state.show_popup_bot = False
        if 'transactions' not in st.session_state:
            st.session_state.transactions = []
    
    def _setup_page_config(self):
        """Configure the Streamlit page settings"""
        st.set_page_config(
            page_title="CGBank - Coimbatore Trusted Banking Partner",
            page_icon="🏦",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def _load_custom_styles(self):
        """Load custom CSS styles"""
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
                padding: 2rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
            }
            .account-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 10px;
                color: white;
                margin: 1rem 0;
            }
            .bot-message {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                color: #333;
                border-left: 4px solid #2a5298;
            }
            .user-message {
                background: #e3f2fd;
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                color: #333;
                border-left: 4px solid #1976d2;
            }
            .popup-bot {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 350px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                z-index: 1000;
            }
            .popup-bot-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            .transaction-item {
                background: white;
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .popup-user-message {
                background: #e3f2fd;
                padding: 8px 12px;
                border-radius: 8px;
                margin: 8px 0;
                margin-left: auto;
                max-width: 80%;
            }
            .popup-bot-message {
                background: #f8f9fa;
                padding: 8px 12px;
                border-radius: 8px;
                margin: 8px 0;
                max-width: 80%;
            }
            .popup-toggle-btn {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1001;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .quick-action-btn {
                margin: 0.2rem 0;
                width: 100%;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_login_page(self):
        """Render the login page"""
        st.markdown("""
        <div class="main-header">
            <h1>🏦 CGBank</h1>
            <h3>Coimbatore Trusted Banking Partner</h3>
            <h4>Secure • Reliable • Innovative</h4>
            <p>174/2 Avinasi road,Annai statue,Coimbatore-641029</p>
            <p>Contact:+91-63820-74060</p>
            <p>Email:Cgbankcbe@gmail.com</p>
            <h5>Welcome to CGBank! Your trusted partner in banking services.</h5> 
            <p>HELPLINE:1800-123-4506</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Login to Your Account")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    try:
                        if CGBankDatabase.verify_user(username, password):
                            st.session_state.logged_in = True
                            st.session_state.current_user = username.lower()  # Store lowercase username
                            st.session_state.page = "dashboard"
                            st.session_state.transactions = CGBankDatabase.get_user_transactions(username)
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password!")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
            
            st.markdown("---")
            st.markdown("**DEMO ACCOUNTS:**")
            st.info("Username: rahul, Password: password123")
            st.info("Username: cravin, Password: mypassword")
    
    def _render_dashboard(self):
        """Render the dashboard page"""
        user = CGBankDatabase.get_user(st.session_state.current_user)
        if not user:
            st.error("User not found!")
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.page = "login"
            st.rerun()
            return
        
        st.markdown(f"""
        <div class="main-header">
            <h1>Welcome back, {user['name']}! 👋</h1>
            <p>Account: {user['account_number']} | {user['account_type']} Account</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="account-card">
                <h3>💰 Account Balance</h3>
                <h2>₹{user['balance']:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="account-card">
                <h3>📊 This Month</h3>
                <h2>₹2,340.50</h2>
                <p>↑ +12.5%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        cols = st.columns(4)
        with cols[0]:
            if st.button("💸 Transfer Money", use_container_width=True):
                st.session_state.page = "transfer"
                st.rerun()
        with cols[1]:
            if st.button("💰 Pay Bills", use_container_width=True):
                st.session_state.page = "bills"
                st.rerun()
        with cols[2]:
            if st.button("📊 Transactions", use_container_width=True):
                st.session_state.page = "transactions"
                st.rerun()
        with cols[3]:
            if st.button("🤖 Chat with Rexa", use_container_width=True):
                st.session_state.page = "rexa"
                st.rerun()
        
        # Spending charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📈 Spending Overview")
            categories = CGBankDatabase.get_spending_categories(st.session_state.current_user)
            df = pd.DataFrame(categories)
            fig = px.pie(df, values='amount', names='name', title="Monthly Spending by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📅 Upcoming Bills")
            bills = CGBankDatabase.get_user_bills(st.session_state.current_user)
            for bill in bills[:3]:
                status_color = "#ffc107" if bill["status"] == "Due Soon" else "#28a745"
                st.markdown(f"""
                <div class="transaction-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0;">{bill['name']}</h4>
                            <p style="margin: 0; color: #6c757d;">Due: {bill['due']}</p>
                        </div>
                        <div style="text-align: right;">
                            <h4 style="margin: 0; color: #dc3545;">₹{bill['amount']:,.2f}</h4>
                            <span style="color: {status_color}; font-size: 0.8em;">{bill['status']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_bot_page(self):
        """Render the chatbot page"""
        st.markdown("""
        <div class="main-header">
            <h1>🤖 Rexa - Your Personal Banking Assistant</h1>
            <p>Ask me anything about your account, transactions, or banking services</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display conversation history
        for conv in st.session_state.bot_conversation[-10:]:
            if isinstance(conv, dict) and 'user' in conv and 'bot' in conv:
                # User message
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong> {conv['user']}
                </div>
                """, unsafe_allow_html=True)
                
                # Bot message
                st.markdown(f"""
                <div class="bot-message">
                    <strong>🤖 Rexa:</strong> {conv['bot']}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Type your message to Rexa:", 
                                     placeholder="Ask me about your account, transactions, or banking services...",
                                     key="chat_input")
            submitted = st.form_submit_button("Send", use_container_width=True)
            
            if submitted and user_input:
                try:
                    # Get bot response
                    bot_response = self.bot.process_message(
                        user_input, 
                        st.session_state.current_user if st.session_state.logged_in else None
                    )
                    
                    # Add to conversation history
                    st.session_state.bot_conversation.append({
                        'user': user_input,
                        'bot': bot_response
                    })
                    
                    # Rerun to update the display
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing message: {str(e)}")

    def _render_popup_bot(self):
        """Render the popup bot interface with built-in banking commands"""
        # Create a toggle button for the popup
        if st.button("💬", key="popup_toggle", help="Chat with Rexa"):
            st.session_state.show_popup_bot = not st.session_state.show_popup_bot
            st.rerun()
        
        # Show the popup if enabled
        if st.session_state.show_popup_bot:
            st.markdown("""
            <div class="popup-bot">
                <div class="popup-bot-header">
                    <h4 style="margin: 0;">🤖 Rexa - Banking Assistant</h4>
                </div>
                <div style="padding: 1rem; max-height: 300px; overflow-y: auto;">
            """, unsafe_allow_html=True)
            
            # Display conversation
            for conv in st.session_state.bot_conversation[-5:]:
                if isinstance(conv, dict) and 'user' in conv and 'bot' in conv:
                    # User message
                    st.markdown(f"""
                    <div class="popup-user-message">
                        <strong>You:</strong> {conv['user']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Bot message
                    st.markdown(f"""
                    <div class="popup-bot-message">
                        <strong>Rexa:</strong> {conv['bot']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Quick actions section with 4 built-in banking commands
            st.markdown("""
                </div>
                <div style="padding: 1rem; border-top: 1px solid #eee;">
                    <p><strong>Quick Banking Commands:</strong></p>
            """, unsafe_allow_html=True)
            
            # Create 4 columns for the commands
            cols = st.columns(2)
            
            with cols[0]:
                # Command 1: Check Balance
                if st.button("💰 Check Balance", key="popup_balance", 
                           help="View your current account balance", 
                           use_container_width=True):
                    self._handle_popup_action("What's my current balance?")
                
                # Command 2: Recent Transactions
                if st.button("📊 Recent Transactions", key="popup_transactions", 
                            help="View your last 5 transactions", 
                            use_container_width=True):
                    self._handle_popup_action("Show my recent transactions")
            
            with cols[1]:
                # Command 3: Transfer Money
                if st.button("💸 Transfer Money", key="popup_transfer", 
                           help="Initiate a money transfer", 
                           use_container_width=True):
                    self._handle_popup_action("I want to transfer money")
                
                # Command 4: Pay Bills
                if st.button("🧾 Pay Bills", key="popup_bills", 
                           help="Pay your pending bills", 
                           use_container_width=True):
                    self._handle_popup_action("I want to pay bills")
            
            # Input form for custom messages
            with st.form("popup_chat_form", clear_on_submit=True):
                user_input = st.text_input("Type your message:", key="popup_input")
                submitted = st.form_submit_button("Send", use_container_width=True)
                
                if submitted and user_input:
                    self._handle_popup_action(user_input)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    def _handle_popup_action(self, message: str):
        """Handle an action from the popup bot"""
        try:
            # Get bot response
            bot_response = self.bot.process_message(
                message, 
                st.session_state.current_user if st.session_state.logged_in else None
            )
            
            # Add to conversation history
            st.session_state.bot_conversation.append({
                'user': message,
                'bot': bot_response
            })
            
            # Rerun to update the display
            st.rerun()
        except Exception as e:
            st.error(f"Error handling popup action: {str(e)}")
    
    def _render_sidebar(self):
        """Render the sidebar navigation"""
        with st.sidebar:
            st.markdown("### 🏦 CGBank Navigation")
            
            if st.session_state.logged_in:
                user = CGBankDatabase.get_user(st.session_state.current_user)
                if not user:
                    st.error("User data not found!")
                    return
                
                st.markdown(f"**Welcome, {user['name']}**")
                st.markdown(f"Account: {user['account_number']}")
                
                if st.button("🏠 Dashboard", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.rerun()
                if st.button("📊 Transactions", use_container_width=True):
                    st.session_state.page = "transactions"
                    st.rerun()
                if st.button("💸 Transfer",  use_container_width=True):
                    st.session_state.page = "transfer"
                    st.rerun()
                if st.button("💰 Bills", use_container_width=True):
                    st.session_state.page = "bills"
                    st.rerun()
                if st.button("🤖 Rexa", use_container_width=True):
                    st.session_state.page = "rexa"
                    st.rerun()
                
                st.markdown("---")
                if st.button("🚪 Logout", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.current_user = None
                    st.session_state.page = "login"
                    st.rerun()
            else:
                st.markdown("Please login to access your account")
    
    def run(self):
        """Run the application"""
        self._render_sidebar()
        
        if st.session_state.logged_in:
            # Render the popup bot (always available when logged in)
            self._render_popup_bot()
            
            # Render the current page
            if st.session_state.page == "dashboard":
                self._render_dashboard()
            elif st.session_state.page == "transactions":
                self._render_transactions_page()
            elif st.session_state.page == "transfer":
                self._render_transfer_page()
            elif st.session_state.page == "bills":
                self._render_bills_page()
            elif st.session_state.page == "rexa":
                self._render_bot_page()
        else:
            self._render_login_page()
    
    def _render_transactions_page(self):
        """Render the transactions page"""
        st.markdown("### 📋 Recent Transactions")
        
        if not st.session_state.transactions:
            st.session_state.transactions = CGBankDatabase.get_user_transactions(st.session_state.current_user)
        
        for txn in st.session_state.transactions[:10]:
            color = "#28a745" if txn['amount'] > 0 else "#dc3545"
            sign = "+" if txn['amount'] > 0 else ""
            
            st.markdown(f"""
            <div class="transaction-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #2a5298;">{txn['description']}</h4>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">
                            {txn['date'].strftime('%Y-%m-%d %H:%M')}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <h3 style="margin: 0; color: {color};">{sign}₹{abs(txn['amount']):,.2f}</h3>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">
                            Balance: ₹{txn['balance']:,.2f}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_transfer_page(self):
        """Render the fund transfer page"""
        st.markdown("### 💸 Transfer Money")
        
        user = CGBankDatabase.get_user(st.session_state.current_user)
        if not user:
            st.error("User data not found!")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Transfer Details")
            with st.form("transfer_form"):
                recipient = st.text_input("Recipient Account", placeholder="Enter account number")
                amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01)
                description = st.text_input("Description (Optional)", placeholder="What's this for?")
                submitted = st.form_submit_button("Transfer", use_container_width=True)
                
                if submitted:
                    try:
                        if amount > 0 and recipient:
                            if amount > user['balance']:
                                st.error("Insufficient funds for this transfer!")
                            else:
                                # Create new transaction
                                new_transaction = {
                                    'date': datetime.now(),
                                    'description': f'Transfer to {recipient}',
                                    'amount': -amount,
                                    'balance': user['balance'] - amount
                                }
                                # Update user balance
                                user['balance'] -= amount
                                # Add to transactions
                                st.session_state.transactions.insert(0, new_transaction)
                                st.success(f"Transfer of ₹{amount:,.2f} to {recipient} initiated successfully!")
                        else:
                            st.error("Please enter valid transfer details!")
                    except Exception as e:
                        st.error(f"Error processing transfer: {str(e)}")
        
        with col2:
            st.markdown("#### Recent Recipients")
            recent_recipients = ["cravin (0987654321)", "rahul (1122334455)", "karthik (5566778899)"]
            for recipient in recent_recipients:
                if st.button(f"📤 {recipient}", key=f"recipient_{recipient}", use_container_width=True):
                    st.info(f"Selected: {recipient}")

    def _render_bills_page(self):
        """Render the bills payment page"""
        st.markdown("### 💰 Pay Bills")
        
        user = CGBankDatabase.get_user(st.session_state.current_user)
        if not user:
            st.error("User data not found!")
            return
        
        bills = CGBankDatabase.get_user_bills(st.session_state.current_user)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Upcoming Bills")
            for bill in bills:
                status_color = "#ffc107" if bill["status"] == "Due Soon" else "#28a745"
                st.markdown(f"""
                <div class="transaction-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0;">{bill['name']}</h4>
                            <p style="margin: 0; color: #6c757d;">Due: {bill['due']}</p>
                        </div>
                        <div style="text-align: right;">
                            <h4 style="margin: 0; color: #dc3545;">₹{bill['amount']:,.2f}</h4>
                            <span style="color: {status_color}; font-size: 0.8em;">{bill['status']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Pay ₹{bill['amount']:,.2f}", key=f"pay_bill_{bill['name']}", use_container_width=True):
                    try:
                        if bill['amount'] > user['balance']:
                            st.error("Insufficient funds to pay this bill!")
                        else:
                            # Create new transaction
                            new_transaction = {
                                'date': datetime.now(),
                                'description': f'Bill Payment: {bill["name"]}',
                                'amount': -bill['amount'],
                                'balance': user['balance'] - bill['amount']
                            }
                            # Update user balance
                            user['balance'] -= bill['amount']
                            # Add to transactions
                            st.session_state.transactions.insert(0, new_transaction)
                            st.success(f"Payment of ₹{bill['amount']:,.2f} for {bill['name']} processed successfully!")
                    except Exception as e:
                        st.error(f"Error processing bill payment: {str(e)}")
        
        with col2:
            st.markdown("#### Pay New Bill")
            with st.form("bill_form"):
                biller = st.selectbox("Select Biller", ["Electricity Company", "Water Department", 
                                                      "Gas Company", "Internet Provider", "Other"])
                if biller == "Other":
                    custom_biller = st.text_input("Enter Biller Name")
                account_num = st.text_input("Account Number")
                bill_amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01)
                submitted = st.form_submit_button("Pay Bill", use_container_width=True)
                
                if submitted and bill_amount > 0:
                    try:
                        if bill_amount > user['balance']:
                            st.error("Insufficient funds to pay this bill!")
                        else:
                            # Create new transaction
                            new_transaction = {
                                'date': datetime.now(),
                                'description': f'Bill Payment: {biller}',
                                'amount': -bill_amount,
                                'balance': user['balance'] - bill_amount
                            }
                            # Update user balance
                            user['balance'] -= bill_amount
                            # Add to transactions
                            st.session_state.transactions.insert(0, new_transaction)
                            st.success(f"Bill payment of ₹{bill_amount:,.2f} processed successfully!")
                    except Exception as e:
                        st.error(f"Error processing bill payment: {str(e)}")

if __name__ == "__main__":
    app = CGBankApp()
    app.run()