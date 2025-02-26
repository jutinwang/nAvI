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
conversation_history = []

# language toggler
language = "english"

def chat_with_bot_stream(user_input):
    global conversation_history
    conversation_history.append({"role": "user", "content": user_input})
    
    if len(conversation_history) == 1:
        conversation_history.insert(0, {
            "role": "system",
            "content": "You are an expert on The Legend of Zelda Ocarina of Time and can give players guidance. You speak like navi but are still clear on steps."
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
    if language == "english":
        lang = "en"
    elif language == "french":
        lang = "fr"
    
    audio_path = tts_generator(chat_history[-1][1], lang)

    mixer.init()
    mixer.music.load(audio_path)
    mixer.music.play()
    while mixer.music.get_busy():  # wait for music to finish playing
        time.sleep(1)

def summarize_conversation(chat_history):
    # Extract only user queries from the chat history
    user_queries = [msg[1] for msg in chat_history if msg[1]]
    # Combine user queries into a single text
    conversation_text = "\n".join(user_queries)
    
    # Generate podcast script
    summary = generate_summary(conversation_text)
    # Convert the script to audio
    audio_path = tts_generator(summary)
    # Return both the script and the audio file path
    return summary, audio_path

def switch_language(option):
    global conversation_history
    print(option == "English")

    if option == "English":
        system_prompt = {
            "role": "system",
            "content": "You are an expert on The Legend of Zelda Ocarina of Time and can give players guidance. You speak like Navi but are still clear on steps. Your responses should all be in english."
        }

        conversation_history = [system_prompt] + [
            msg for msg in conversation_history if msg["role"] != "system"
        ]

    elif option == "French":
        system_prompt = {
            "role": "system",
            "content": "You are an expert on The Legend of Zelda Ocarina of Time and can give players guidance. You speak like Navi but are still clear on steps. Your responses should all be in french."
        }
        
        conversation_history = [system_prompt] + [
            msg for msg in conversation_history if msg["role"] != "system"
        ]

TITLE = """
<style>
h1 { text-align: center; font-size: 24px; margin-bottom: 10px; }
</style>
<h1>Hey, Look! I'm Navi!</h1>
"""

TITLE_Summary = """
<style>
h1 { text-align: center; font-size: 24px; margin-bottom: 10px; }
</style>
<h1>🫗 Let Me Summarize Your Story! </h1>
"""

with gr.Blocks(theme=gr.themes.Glass(primary_hue="violet", secondary_hue="violet", neutral_hue="stone")) as demo:
    with gr.Tabs():
        with gr.TabItem("💬Chat"):
            gr.HTML(TITLE)
            # language_toggle = gr.Button("En/Fr")
            language_toggle = gr.Dropdown(["English", "French"], label="Choose a language")

            chatbot = gr.Chatbot(label="Navi")
            with gr.Row():
                user_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Hey Look! Listen Here!",
                    lines=1
                )
                send_button = gr.Button("Help!")
                tts_button = gr.Button("Read Recent Message")
            
            send_button.click(
                fn=chat_with_bot_stream,
                inputs=user_input,
                outputs=chatbot,
                queue=True
            ).then(
                fn=lambda: "",
                inputs=None,
                outputs=user_input
            )

            tts_button.click(
                fn=tts,
                inputs=chatbot,
            )

            # language_toggle.click(
            #     fn=switch_language,
            # )

            language_toggle.change(switch_language, inputs=language_toggle, outputs=None)
        
        with gr.TabItem("📜 Dungeon Solver"):
            gr.Markdown("## Solve a Dungeon!")
            gr.Markdown('Choose a dungeon to solve:')
            
            storyboard_output = gr.Textbox(label="Generated Storyboard", interactive=False)
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

        with gr.TabItem("Summarize My Adventure"):
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

demo.launch()