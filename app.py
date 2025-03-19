import gradio as gr
import os
from groq import Groq
from dotenv import load_dotenv
import tempfile
import time
from pygame import mixer

from audio import tts_generator
from summarizer import generate_summary

# Load env variables
load_dotenv()

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Initialize conversation history
# Initialize conversation history
conversation_history = []

def clear_chat():
    global conversation_history
    conversation_history = []  # Reset history when page loads
    return []

# language toggler
language = "English"
region = "Canada"
measurement_system = "metric"
temperature = "celsius"
weight = "grams and kilograms"
date_format = "YYYY - MM - DD"

def chat_with_bot_stream(user_input):
    conversation_history.append({"role": "user", "content": user_input})
    
    if len(conversation_history) == 1:
        conversation_history.insert(0, {
            "role": "system",
            "content": f"""
            You are an expert on The Legend of Zelda Ocarina of Time and can give players guidance. 
            You speak like navi but are still clear on steps.
            You provide in depth answers to long questions.
            You speak in short answers for simple 1 word or simple sentences.
            Always respond to messages using only {language} even if the user talks in a different language.
            Your region is set to the {region}.
            Whenever there are measurements, you will use the {measurement_system} system.
            When you need to display the temperature, you will use {temperature}.
            Mass will be measured in all iterations of {weight}.
            You will dates in the format: {date_format}.
            """
        },)
    
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=conversation_history,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    
    response_content = ""
    for chunk in completion:
        response_content += chunk.choices[0].delta.content or ""
    
    conversation_history.append({"role": "assistant", "content": response_content})
    
    return [(msg["content"] if msg["role"] == "user" else None, 
             msg["content"] if msg["role"] == "assistant" else None) 
            for msg in conversation_history]

# Function to generate a system prompt based on the selected dungeon
def generate_system_prompt(dungeon_name):
    return f"""You are Navi from The Legend of Zelda: Ocarina of Time. Your task is to guide the player through {dungeon_name}. Provide clear and step-by-step instructions in Navi's voice. Stay in character and be helpful!"""

def solve_dungeon(system_prompt, user_message):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    completion = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=messages,
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
    )
    
    # Access the result using .choices and .message instead of subscripting
    return completion.choices[0].message.content

def tts(chat_history):
    global language
    lang = "en"
    # Convert the script to audio
    if language == "English":
        lang = "en"
    elif language == "French":
        lang = "fr"
    
    audio_path = tts_generator(chat_history[-1][1], lang)

    mixer.init()
    mixer.music.load(audio_path)
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)

def summarize_conversation(chat_history):
    global language
    lang = "en"
    # Convert the script to audio
    if language == "English":
        lang = "en"
    elif language == "French":
        lang = "fr"

    user_queries = [content for msg in chat_history for content in msg if content]
    conversation_text = "\n".join(user_queries)
    
    summary = generate_summary(conversation_text, language)
    audio_path = tts_generator(summary, lang)

    return summary, audio_path

def switch_language(option):
    global language
    print(option == "English")

    language = option

    update_system_prompt()

def switch_regions(option):
    global region, measurement_system, temperature, weight, date_format

    if option == "Canada":
        region = "Canada"
        measurement_system = "metric"
        temperature = "celsius"
        weight = "grams and kilograms"
        date_format = "YYYY - MM - DD"

    elif option == "USA":
        region = "United States of America"
        measurement_system = "imperial"
        temperature = "fahrenheit"
        weight = "pounds"
        date_format = "MM/DD/YYYY"

    else:
        region = "International"
        measurement_system = "metric"
        temperature = "celsius"
        weight = "grams and kilograms"
        date_format = "YYYY-MM-DD"

    update_system_prompt()


def update_system_prompt():
    global conversation_history, region, language, measurement_system, temperature, weight

    system_prompt = {
            "role": "system",
            "content": f"""
            You are an expert on The Legend of Zelda Ocarina of Time and can give players guidance. 
            You speak like navi but are still clear on steps.
            You provide in depth answers to long questions.
            You speak in short answers for simple 1 word or simple sentences.
            Always respond to messages using only {language} even if the user talks in a different language.
            Your region is set to the {region}.
            Whenever there are measurements, you will use the {measurement_system} system.
            When you need to display the temperature, you will use {temperature}.
            Mass will be measured in all iterations of {weight}.
            You will dates in the format: {date_format}.
            """
    }
    conversation_history = [system_prompt] + [
        msg for msg in conversation_history if msg["role"] != "system"
    ]

# ******************** Maybe Add ********************
# def clear_history():
#     global conversation_history
#     if conversation_history and conversation_history[0]["role"] == "system":
#         conversation_history = [conversation_history[0]]  # Keep only the system prompt
#     else:
#         conversation_history = []  # If no system prompt exists, clear everything


theme = gr.themes.Ocean(
    primary_hue=gr.themes.Color(c100="#003ab5", c200="#002973", c300="#002973", c400="#00206b", c50="#013aba", c500="#001f63", c600="#00104a", c700="#001042", c800="#00103a", c900="#040c2c", c950="#000821"),
    secondary_hue=gr.themes.Color(c100="#426bc5", c200="#3f65b7", c300="#3a63a5", c400="#2d457f", c50="#4a7bd6", c500="#29427b", c600="#294173", c700="#192952", c800="#192952", c900="#213152", c950="#203152"),
    neutral_hue=gr.themes.Color(c100="#e0f2fe", c200="#bae6fd", c300="#7dd3fc", c400="#38bdf8", c50="#f0f9ff", c500="#0ea5e9", c600="#0284c7", c700="#0369a1", c800="#66a9e8", c900="#b2f4fc", c950="#66a9e8"),
    text_size="lg",	
    font=['Italiana', 'ui-sans-serif', gr.themes.GoogleFont('system-ui'), 'sans-serif'],
).set(
    body_background_fill='linear-gradient(120deg, *primary_950 0%, *primary_950 45%, *primary_800 65%, *primary_500 85%, *primary_50 100%)',
    body_background_fill_dark='linear-gradient(120deg, *primary_950 0%, *primary_950 45%, *primary_800 65%, *primary_500 85%, *primary_50 100%)',
    body_text_color='*neutral_50',
    body_text_color_dark='*neutral_50',
    input_background_fill='*neutral_700',
    background_fill_primary="*primary_300",
    background_fill_secondary='*primary_500',
    background_fill_secondary_dark='*primary_500',
    color_accent='*secondary_50',
    color_accent_soft='*neutral_800',
    color_accent_soft_dark='*neutral_800',
    link_text_color='*secondary_50',
    link_text_color_active_dark='*neutral_100',
    code_background_fill='*neutral_300',
    code_background_fill_dark='*primary_950',
    block_background_fill='*primary_900',
    block_background_fill_dark='*primary_900',
    block_info_text_color='*neutral_50 ',
    block_info_text_color_dark='*neutral_50',
    block_label_background_fill='*neutral_500',
    block_label_background_fill_dark='*neutral_500',
    block_label_text_color='*primary_400',
    block_label_text_color_dark='*primary_400',
    block_title_text_color='*neutral_100',
    block_title_text_color_dark='*neutral_100',
    accordion_text_color='*neutral_50',
    accordion_text_color_dark='*neutral_50',
    button_primary_background_fill='linear-gradient(120deg, *secondary_600 0%, *secondary_600 30%, *primary_500 70%, *primary_600 100%)',
    button_primary_background_fill_dark='linear-gradient(120deg, *secondary_600 0%, *secondary_600 30%, *primary_500 70%, *primary_600 100%)',
    button_primary_text_color='*neutral_100',
    button_primary_text_color_dark='*neutral_100',
    button_secondary_background_fill='linear-gradient(120deg, *secondary_950 0%, *secondary_800 40%, *secondary_500 70%, *secondary_50 100%)',
    button_secondary_background_fill_dark='linear-gradient(120deg, *secondary_950 0%, *secondary_800 40%, *secondary_500 70%, *secondary_50 100%)',
    button_primary_background_fill_hover='linear-gradient(120deg, *secondary_500 0%, *secondary_500 30%, *primary_400 70%, *primary_500 100%)',
    button_secondary_background_fill_hover='linear-gradient(120deg, *secondary_500 0%, *secondary_500 30%, *primary_400 70%, *primary_500 100%)',
    button_secondary_text_color='*neutral_100',
    button_secondary_text_color_dark='*neutral_100',
)



TITLE = """
<style>
.container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px; /* Space between image and text */
}

.container img {
    height: 50px; /* Match text size */
}

h1 {
    font-size: 24px;
    margin: 0;
}
</style>

<div class="container">
    <img src='/gradio_api/file=navi_logo.png'>
    <h1>Hey, Look! I'm Navi!</h1>
</div>
"""

SUB_TITLE = """
<style>
    h4 { 
        text-align: center; 
        font-size: 14px;
    }
    .container {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .padding.svelte-phx28p {
        padding: 0; /* Ensures no extra padding */
    }
</style>

<div class="container">
    <h4>Ask nAvI all your Ocarina of Time questions!</h4>
</div>
"""

TITLE_Summary = """
<style>
h1 { text-align: center; font-size: 24px; margin-bottom: 10px; }
</style>
<h1>🗡️🛡️ Let Me Summarize Your Story! </h1>
<br>
Hey, Listen! Let me summarize our previous conversation so you can reflect on what we accomplished. I just know we'll save Hyrule!
"""

with gr.Blocks(theme=theme) as demo:
    with gr.Tabs():
        with gr.TabItem("💬 Chat"):
            gr.HTML(TITLE)
            
            # Dropdowns
            with gr.Row():
                country_tottle = gr.Dropdown(["Canada", "USA", "International"], label="Region")
                language_toggle = gr.Dropdown(["English", "French"], label="Choose a language")

            chatbot = gr.Chatbot(label="Navi")

            # Clear chat on refresh
            demo.load(clear_chat, inputs=None, outputs=chatbot)

            with gr.Row():
                user_input = gr.Textbox(label="Your Message", placeholder="Hey Look! Listen Here!", lines=1, scale=8)
                send_button = gr.Button("Send", elem_id="send_button", scale=1)

            send_button.click(fn=chat_with_bot_stream, inputs=user_input, outputs=chatbot, queue=True).then(
                fn=lambda: "", inputs=None, outputs=user_input
            )

            country_tottle.change(switch_regions, inputs=country_tottle, outputs=None)
            language_toggle.change(switch_language, inputs=language_toggle, outputs=None)

            # Custom CSS for circular send button
            '''demo.css = """
            #send_button {
                background-color: #0084ff;
                color: white;
                border-radius: 50%;
                font-size: 20px;
                width: 50px;
                height: 50px;
                text-align: center;
                line-height: 50px;
                border: none;
                cursor: pointer;
            }
            """
            '''

        with gr.TabItem("📜 Dungeon Solver"):
            gr.Markdown("## Solve a Dungeon!")
            #gr.Markdown("Hey! It's dangerous out there. Let me help you solve one of the pesky dungeons!")
            gr.Markdown('#### Choose a dungeon to solve:')
            
            storyboard_output = gr.Textbox(label="Dungeon Info", interactive=False)
            user_input_box = gr.Textbox(label="Your Question", placeholder="Ask Navi about this dungeon!")
            
            for dungeon in [
                "Inside the Deku Tree", "Dodongo’s Cavern", "Inside Jabu-Jabu’s Belly", 
                "Forest Temple", "Fire Temple", "Water Temple", "Shadow Temple", 
                "Spirit Temple", "Ganon’s Castle"]:
                
                dungeon_button = gr.Button(dungeon)
                dungeon_button.click(
                    fn=lambda dungeon_name, user_input: solve_dungeon
                (generate_system_prompt(dungeon_name), user_input),
                    inputs=[gr.Textbox(value=dungeon, visible=False), user_input_box],
                    outputs=storyboard_output
                )

        with gr.TabItem("🌟Summarize My Adventure"):
            gr.HTML(TITLE_Summary)
            summary_button = gr.Button("Summarize!")
            summary_script_output = gr.Textbox(label="Transcript of Summary", placeholder="Summary Here.", lines=5)
            summary_audio_output = gr.Audio(label="Summary Audio")
            
            # Generate podcast script and audio
            summary_button.click(
                fn=summarize_conversation,  # This should be defined in your actual application
                inputs= chatbot,  # Pass the chat history
                outputs=[summary_script_output, summary_audio_output]
            )

demo.launch(allowed_paths=["navi_logo.png"], share=False)