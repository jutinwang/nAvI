# podcast_generator.py

from groq import Groq
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def generate_summary(topic, language):
    if not topic.strip():
        return "Please provide a topic from the chatbot response to generate the script."
    
    messages = [
        {
            "role": "system",
            "content":  f"""
                        Start by introducing yourself as nAvI, and tell the listener you're a fairy that helps adventurers of any kind in beating the game Ocarina of Time and stopping Ganon.
                        You are an expert on The Legend of Zelda Ocarina of Time and can give players guidance. You speak like navi but are still clear on steps.
                        Write the script in {language}.
                        This summary is based on conversations you've had with the user already.
                        Theirs a lot of information, and if the user is here, treat them nicely and be patient with them as it's a lot of information to understand
                        Speak in a warm, educational tone as if you’re sharing valuable, easy-to-understand summaries.
                        Go over the events you talked about already in chronilogical order of events from earliest in the game to later. 
                        Conclude the summary of what the player can do next based on their current situation.
                        Keep the episode brief, under 60 seconds, and introduce yourself as nAvI, the hero's magical fairy guide in saving Hyrule.
                        Use casual fillers for a natural, approachable flow, without background music or extra frills.
                        """
        },
        {
            "role": "user",
            "content": f"{topic}"
        }
    ]

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    script_content = ""
    for chunk in completion:
        script_content += chunk.choices[0].delta.content or ""

    return script_content