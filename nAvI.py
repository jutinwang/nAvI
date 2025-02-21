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

TITLE = """
<style>
h1 { text-align: center; font-size: 24px; margin-bottom: 10px; }
</style>
<h1>Hey, Look! I'm Navi!</h1>
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
                send_button = gr.Button("Help!")
            
            send_button.click(
                fn=lambda x: "Navi: " + x,
                inputs=user_input,
                outputs=chatbot,
                queue=True
            ).then(
                fn=lambda: "",
                inputs=None,
                outputs=user_input
            )
        
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

demo.launch()