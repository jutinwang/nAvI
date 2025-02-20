import gradio as gr
import os
from groq import Groq
from dotenv import load_dotenv  

# Load env variables
load_dotenv()

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Initialize conversation history
conversation_history = []

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

# Function to generate a storyboard
def generate_storyboard(scenario):
    f = open("test.txt", "r") # https://gamefaqs.gamespot.com/n64/197771-the-legend-of-zelda-ocarina-of-time/faqs/20240
    if not scenario.strip():
        return "Hey Look! I'm here to to help, ask me if you have any questions ok?"
    
    messages = [
        {"role": "system", "content": """You are an expert on The Legend of Zelda Ocarina of Time and can give players guidance. You speak like navi but are still clear on steps."""},
        {"role": "user", "content": f"Answer my question about the legend of zelda ocarina of time: {f.read()}"}
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
    return completion.choices[0].message.content 


TITLE = """
<style>
h1 { text-align: center; font-size: 24px; margin-bottom: 10px; }
</style>
<h1>📖 Storyboard Assistant</h1>
"""

with gr.Blocks(theme=gr.themes.Glass(primary_hue="violet", secondary_hue="violet", neutral_hue="stone")) as demo:
    with gr.Tabs():
        with gr.TabItem("💬Chat"):
            gr.HTML(TITLE)
            chatbot = gr.Chatbot(label="Navi")
            with gr.Row():
                user_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Hey Look! Listen Here!",
                    lines=1
                )
                send_button = gr.Button("HYAHH!????")
            
            # Chatbot functionality
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
        
        with gr.TabItem("📖 Generate Storyboard"):
            gr.Markdown("## Generate a Storyboard")
            scenario_input = gr.Textbox(label="Enter your scenario")
            generate_btn = gr.Button("Generate Storyboard")
            storyboard_output = gr.Textbox(label="Generated Storyboard", interactive=False)
            generate_btn.click(generate_storyboard, inputs=scenario_input, outputs=storyboard_output)

demo.launch()