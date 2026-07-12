import os
import json
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Learning Buddy - Socrates",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Global Font Settings */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }

    /* Gradient Title */
    .gradient-title {
        background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800;
        margin-bottom: 5px;
    }
    
    .subtitle {
        font-size: 1.25rem;
        color: #6b7280;
        margin-bottom: 25px;
        font-weight: 400;
    }

    /* Custom Cards */
    .premium-card {
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(124, 58, 237, 0.15);
        background: rgba(124, 58, 237, 0.03);
        margin-bottom: 20px;
        box-shadow: 0 4px 20px -2px rgba(124, 58, 237, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .premium-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px -2px rgba(124, 58, 237, 0.1);
        border-color: rgba(124, 58, 237, 0.3);
    }
    
    /* Styled Badge */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
        color: white;
        margin-bottom: 12px;
    }
    
    /* Sidebar styling tweaks */
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }

    /* Tab Custom Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- MOCK DATA FOR BINARY SEARCH -----------------
mock_explanation = """
### Understanding Binary Search

Imagine you are looking for a specific name in a printed physical directory containing 1,000 alphabetically sorted names. If you start from the first page and read line-by-line, that is called **Linear Search**. If the name is at the end, it will take you 1,000 steps.

**Binary Search** is a much smarter, faster way to search, but it has one strict rule: **the list must be sorted** (alphabetically, numerically, etc.).

#### How It Works:
1. **Find the Middle**: Open the directory directly to the exact middle page.
2. **Compare**: Check the name on that middle page.
   - If the name you want comes *before* the middle page name alphabetically, you know it must be in the first half.
   - If the name comes *after* the middle page name, it must be in the second half.
3. **Discard Half**: You can completely ignore the other half. Your search space has now shrunk from 1,000 names to 500!
4. **Repeat**: Repeat this exact process on the remaining half. 500 becomes 250, then 125, then 62, and so on.

Within just **10 steps** (since $2^{10} = 1024$), you can find any name among 1,000 elements!
"""

mock_example = """
### The Classic Guessing Game Analogy

Suppose I ask you to guess a number I am thinking of between **1 and 100**.
Each time you make a guess, I will only tell you if your guess is **too high**, **too low**, or **correct**.

* **Inefficient Strategy (Linear Search)**: You guess 1, then 2, then 3, then 4... If my number is 99, it takes you 99 guesses.
* **Optimal Strategy (Binary Search)**:
  1. You guess **50** (the middle).
  2. I say: *"Too low!"*
  3. You immediately throw away all numbers from 1 to 50. Now your search space is **51 to 100**.
  4. You guess the middle of that: **75**.
  5. I say: *"Too high!"*
  6. You throw away all numbers from 75 to 100. Now your search space is **51 to 74**.
  7. You guess the middle: **62**.

By always choosing the middle, you halve the search window every single time. Even if you are extremely unlucky, you will guess the number in **7 guesses or fewer** ($2^7 = 128$).
"""

mock_quiz = [
    {
        "question": "What is the most critical prerequisite for performing a Binary Search on a list?",
        "options": [
            "The list must contain only numbers",
            "The list must be sorted",
            "The list must have an odd number of elements",
            "The list must be empty"
        ],
        "answer_index": 1,
        "explanation": "Binary search relies on order to determine whether to search the left half or right half of the list."
    },
    {
        "question": "In the worst-case scenario, how does the remaining search space change with each step?",
        "options": [
            "It decreases by 1 element",
            "It decreases by 10 elements",
            "It is cut in half",
            "It doubles in size"
        ],
        "answer_index": 2,
        "explanation": "Binary search eliminates half of the remaining items at each stage."
    },
    {
        "question": "If you are searching for 12 in the sorted list [2, 5, 8, 12, 16, 23, 38, 56, 72], what is the first number compared?",
        "options": [
            "2 (First index)",
            "16 (Middle index)",
            "12 (Target value)",
            "72 (Last index)"
        ],
        "answer_index": 1,
        "explanation": "The list has 9 elements. The middle index is index 4 (the fifth element), which corresponds to 16."
    },
    {
        "question": "What is the maximum number of comparisons needed to find an item in a sorted list of 1,000 elements?",
        "options": [
            "1000",
            "500",
            "10",
            "1"
        ],
        "answer_index": 2,
        "explanation": "Since 2^10 = 1024, it takes at most 10 cuts to reduce a 1,000-element list to a single item."
    },
    {
        "question": "In which of the following scenarios is Binary Search NOT applicable?",
        "options": [
            "Finding a contact in an alphabetically sorted contact list",
            "Finding a specific temperature value in a sorted array",
            "Finding a book by ID in a database sorted by book ID",
            "Finding the highest-scoring student in an unsorted pile of papers"
        ],
        "answer_index": 3,
        "explanation": "If the list of papers is unsorted, you cannot determine which direction to search from the midpoint."
    }
]

# ----------------- SESSION STATE INITS -----------------
if "current_content" not in st.session_state:
    st.session_state.current_content = {
        "explanation": mock_explanation,
        "example": mock_example,
        "quiz": mock_quiz
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "last_topic" not in st.session_state:
    st.session_state.last_topic = "Binary Search"

# ----------------- SIDEBAR CONFIG -----------------
st.sidebar.markdown("### 🛠️ Configuration")

# API Key handling
env_api_key = os.environ.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=env_api_key,
    type="password",
    help="Enter your Google Gemini API Key. Get one from Google AI Studio."
)

model_name = st.sidebar.selectbox(
    "Gemini Model",
    ["gemini-3.5-flash", "gemini-3.1-flash-lite"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎓 Learning Buddy Customization")

topic = st.sidebar.text_input(
    "Learning Topic",
    value="Binary Search",
    help="Define the topic the AI Buddy will teach."
)

buddy_name = st.sidebar.text_input(
    "Buddy Persona Name",
    value="Socrates the Searcher"
)

# Standardized Persona Prompts (reusable for any topic)
system_prompt = f"""You are {buddy_name}, a patient, encouraging computer science tutor. Your goal is to help the user understand the concept of {topic}.
Follow these rules:
1. Do NOT just give the student the answer. Instead, ask guided questions to lead them to the answer (the Socratic method).
2. Explain concepts in simple, plain language. Avoid jargon unless you define it first.
3. Use real-life analogies, like looking up a word in an alphabetical dictionary, to make the concept concrete.
4. Provide positive reinforcement and constructive feedback on their responses.
5. Always check understanding and ask them to explain a small part back to you or solve a simple mini-puzzle before moving on to more complex details.
"""

with st.sidebar.expander("👁️ View System/Persona Prompt"):
    st.code(system_prompt, language="text")

# Helper function to call Gemini API with automatic fallback for high-demand spikes (503)
def get_gemini_response(prompt_text, system_instruction_text=None, is_json=False):
    if not api_key:
        return None
        
    # List of active models on user key to try in sequence if one fails
    models_to_try = [model_name]
    for fallback in ["gemini-3.1-flash-lite", "gemini-2.0-flash"]:
        if fallback not in models_to_try:
            models_to_try.append(fallback)
            
    last_error = None
    for model in models_to_try:
        try:
            client = genai.Client(api_key=api_key)
            config = types.GenerateContentConfig()
            if system_instruction_text:
                config.system_instruction = system_instruction_text
            if is_json:
                config.response_mime_type = "application/json"
                
            response = client.models.generate_content(
                model=model,
                contents=prompt_text,
                config=config
            )
            return response.text
        except Exception as e:
            last_error = e
            # Log the fallback trial in Streamlit sidebar info
            st.sidebar.info(f"🔄 Model {model} busy or failed. Trying fallback...")
            continue
            
    st.error(f"Error calling Gemini API: {str(last_error)}")
    return None

# Combined generation function
def generate_all_topic_materials():
    if not api_key:
        st.sidebar.warning("⚠️ Please provide a Gemini API Key to generate content.")
        return

    # Reset chat and quiz state for the new topic
    st.session_state.messages = []
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.last_topic = topic

    with st.sidebar:
        with st.spinner(f"Generating full curriculum for {topic}..."):
            combined_prompt = f"""You are an expert curriculum builder. Generate beginner-friendly learning materials for the topic: "{topic}".
Return a JSON object with exactly the following keys and structures:
- "explanation": string (A detailed markdown explanation of the concept of {topic}. Use subheadings, bullet points, and highlight key terms. Explain it in simple terms, avoiding complex jargon.)
- "example": string (A detailed markdown description of one concrete, real-life example or analogy that intuitively illustrates how {topic} works. Make it relatable and engaging, without showing code.)
- "quiz": list of 5 multiple-choice questions, where each question is a JSON object with:
  - "question": string (the question text)
  - "options": list of 4 strings (multiple choice options)
  - "answer_index": integer (0 for the first option, 1 for second, 2 for third, 3 for fourth)
  - "explanation": string (a brief explanation of why the correct option is right)
Ensure the JSON is strictly valid, does not contain comments, and conforms to this structure.
"""
            response = get_gemini_response(combined_prompt, is_json=True)
            if response:
                try:
                    cleaned = response.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()
                    
                    parsed = json.loads(cleaned)
                    st.session_state.current_content = parsed
                    st.sidebar.success("🎉 All materials loaded!")
                except Exception as e:
                    st.sidebar.error(f"Error parsing curriculum JSON: {str(e)}")

# Sidebar Load Button
load_btn = st.sidebar.button("🎓 Load Topic & Generate All", type="primary", on_click=generate_all_topic_materials)

# Detect if topic name reverted to default to reset mock data
if topic.lower() == "binary search" and st.session_state.last_topic != "Binary Search" and st.session_state.current_content.get("explanation") != mock_explanation:
    st.session_state.current_content = {
        "explanation": mock_explanation,
        "example": mock_example,
        "quiz": mock_quiz
    }
    st.session_state.messages = []
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.last_topic = "Binary Search"

# ----------------- MAIN UI -----------------
st.markdown('<div class="gradient-title">🎓 AI Learning Buddy</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Meet <b>{buddy_name}</b>, your interactive guide to mastering <b>{topic}</b>.</div>', unsafe_allow_html=True)

# Tabs definition
tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Explain Concept",
    "💡 Real-Life Example",
    "🧠 Take a Quiz",
    "💬 Chat with Tutor"
])

# ----------------- TAB 1: EXPLAIN CONCEPT -----------------
with tab1:
    st.markdown("### Learn the Core Concept")
    
    if st.session_state.current_content:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<span class="badge">Explanation</span>', unsafe_allow_html=True)
        st.markdown(st.session_state.current_content["explanation"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👈 Enter a topic and click 'Load Topic & Generate All' in the sidebar.")

# ----------------- TAB 2: REAL-LIFE EXAMPLE -----------------
with tab2:
    st.markdown("### Real-Life Analogy")
    
    if st.session_state.current_content:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<span class="badge">Real-life Analogy</span>', unsafe_allow_html=True)
        st.markdown(st.session_state.current_content["example"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👈 Enter a topic and click 'Load Topic & Generate All' in the sidebar.")

# ----------------- TAB 3: TAKE A QUIZ -----------------
with tab3:
    st.markdown("### Test Your Understanding")
    
    if st.session_state.current_content and "quiz" in st.session_state.current_content:
        st.write("Take this 5-question quiz to check your comprehension. Submit your answers at the end for immediate feedback.")
        quiz = st.session_state.current_content["quiz"]
        
        # Display questions
        for idx, q in enumerate(quiz):
            st.markdown(f"#### **Question {idx+1}: {q['question']}**")
            
            # Key to keep state of radio selection
            radio_key = f"q_{idx}"
            
            selected_option = st.radio(
                "Choose one option:",
                q['options'],
                key=radio_key,
                index=None,
                label_visibility="collapsed"
            )
            
            if selected_option:
                st.session_state.quiz_answers[idx] = q['options'].index(selected_option)
            st.markdown("<br>", unsafe_allow_html=True)
            
        submit_btn = st.button("📝 Submit Answers", type="primary")
        
        if submit_btn or st.session_state.quiz_submitted:
            st.session_state.quiz_submitted = True
            
            # Grade answers
            correct_count = 0
            st.markdown("### 📊 Quiz Results & Feedback")
            
            for idx, q in enumerate(quiz):
                user_choice = st.session_state.quiz_answers.get(idx, None)
                correct_idx = q['answer_index']
                
                st.markdown(f"**Question {idx+1}: {q['question']}**")
                
                if user_choice is None:
                    st.warning("⚠️ You did not answer this question.")
                elif user_choice == correct_idx:
                    correct_count += 1
                    st.success(f"✅ **Correct!** You selected: *{q['options'][user_choice]}*")
                    st.markdown(f"*{q['explanation']}*")
                else:
                    st.error(f"❌ **Incorrect.** You selected: *{q['options'][user_choice]}*")
                    st.markdown(f"👉 **Correct Answer**: *{q['options'][correct_idx]}*")
                    st.markdown(f"*{q['explanation']}*")
                st.markdown("---")
            
            # Display Score
            score_percent = int((correct_count / len(quiz)) * 100)
            col1, col2, col3 = st.columns(3)
            col1.metric("Score", f"{correct_count} / {len(quiz)}", f"{score_percent}%")
            
            if score_percent == 100:
                st.balloons()
                st.success("🏆 Perfect Score! You've mastered this topic's basics!")
            elif score_percent >= 60:
                st.info("👍 Good job! Review the incorrect questions to solidify your understanding.")
            else:
                st.warning("📚 Keep practicing! Re-read the explanation or chat with Socrates to clear up doubts.")
                
            if st.button("🔄 Retake Quiz"):
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
    else:
        st.info("👈 Enter a topic and click 'Load Topic & Generate All' in the sidebar.")

# ----------------- TAB 4: CHAT WITH TUTOR -----------------
with tab4:
    st.markdown(f"### Interactive Discussion with {buddy_name}")
    st.write(f"Talk with {buddy_name} in real-time using the Socratic method. Test your theories, ask questions, and get feedback.")
    
    # Initialize chatbot messages if empty
    if not st.session_state.messages:
        welcome_message = f"Hello there! I'm {buddy_name}, your guide to understanding algorithms. Today, we're going to explore a very powerful concept called **{topic}**. Before we dive in, let me ask: have you ever heard of it, or do you have any guess as to what it might be?"
        st.session_state.messages = [{"role": "assistant", "content": welcome_message}]
        
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # User Chat Input
    if user_input := st.chat_input("Type your response here..."):
        # Append User input
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        # Get response
        if api_key:
            with st.spinner(f"{buddy_name} is typing..."):
                # Compile chat history to feed as prompt
                chat_context = []
                for msg in st.session_state.messages:
                    role_tag = "Student" if msg["role"] == "user" else "Tutor"
                    chat_context.append(f"{role_tag}: {msg['content']}")
                
                full_prompt = "\n".join(chat_context) + f"\nTutor ({buddy_name}):"
                
                response = get_gemini_response(full_prompt, system_instruction_text=system_prompt)
                
                if response:
                    # Clean response prefix if AI generates "Tutor (Socrates): text"
                    prefix_to_clean = f"Tutor ({buddy_name}):"
                    clean_response = response.strip()
                    if clean_response.startswith(prefix_to_clean):
                        clean_response = clean_response[len(prefix_to_clean):].strip()
                        
                    st.session_state.messages.append({"role": "assistant", "content": clean_response})
                    with st.chat_message("assistant"):
                        st.markdown(clean_response)
        else:
            # Mock conversation flow if no API key
            with st.chat_message("assistant"):
                mock_responses = {
                    "i think it's a way to search for things in a list, like looking for a number, but i don't know how it works.": 
                        "Spot on! It is indeed a way to search for items in a list. Imagine you have a physical English dictionary and you are looking for the word **'Search'**. How would you find it? Would you start on page 1 and read word-by-word until you reach 'Search'?",
                    "no, that would take forever. i'd open the dictionary somewhere in the middle, see what letter it is, and then go forward or backward depending on where 's' is.":
                        "Exactly! That is a brilliant intuition. You just described the core idea of Binary Search! By opening to the middle, you check the word there. If your target letter 'S' comes after that word, what can you say about all the pages in the first half of the dictionary? Do you need to look at them?",
                    "no, because 's' has to be after them since the dictionary is alphabetical. so i can throw away the first half!":
                        "Precisely! You throw away half of the remaining pages in one single step. That's why it is called **'binary'** (halving into two parts). But there is a crucial catch: why does this trick work for a dictionary, but wouldn't work if I gave you a pile of unsorted papers?",
                    "because the dictionary is in alphabetical order. if the pages were unsorted, opening in the middle wouldn't tell me where to go next.":
                        "Magnificent! You hit the most important rule of Binary Search: **the list must be sorted** beforehand. You've mastered the basic intuition. Try testing this out by taking the **Take a Quiz** tab above!",
                }
                
                # Normalize key
                normalized_input = user_input.lower().strip()
                if normalized_input in mock_responses:
                    resp = mock_responses[normalized_input]
                    st.session_state.messages.append({"role": "assistant", "content": resp})
                    st.markdown(resp)
                else:
                    fallback_resp = f"That's an interesting thought! As a Socratic tutor, I want you to think about how we throw away half of our options at each step. (Add a Gemini API Key in the sidebar to chat dynamically about any response!)"
                    st.session_state.messages.append({"role": "assistant", "content": fallback_resp})
                    st.markdown(fallback_resp)
