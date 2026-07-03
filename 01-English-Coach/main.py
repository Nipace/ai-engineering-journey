from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

message = input("Enter a message: ")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are an English communication coach."
        },
        {
            "role": "user",
            "content": f"""
Classify this message as:
- Professional
- Casual
- Needs Improvement

Then explain why and rewrite it professionally.

Message:
{message}
"""
        }
    ]
)

print(response.choices[0].message.content)