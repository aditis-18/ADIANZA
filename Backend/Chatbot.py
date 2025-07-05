# Import necessary modules
from groq import Groq                         # Import Groq client to interact with the Groq API
from json import load, dump                   # Import functions to read and write JSON files
import datetime                               # Import datetime to get current date and time
from dotenv import dotenv_values              # Import to read environment variables from .env file

# Load environment variables from the .env file
env_vars = dotenv_values(".env")

# Get required variables from the .env file
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq API client with the API key
client = Groq(api_key=GroqAPIKey)

# Initialize the messages list for conversation history
messages = []

# System message defines the chatbot's behavior and constraints
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# Initialize the system instructions for the chatbot
SystemChatBot =[
    {"role": "system", "content": System}
]

# Try to load previous chat history from ChatLog.json
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    # If the file does not exist, create an empty one
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to get the current date and time in a formatted string
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    # Format the real-time information string
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours: {minute} minutes: {second} seconds.\n"
    return data

# Function to clean up the answer by removing empty lines
def AnswerModifier(Answer):
    lines = Answer.split('\n')    
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Main function to interact with the chatbot
def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response."""

    try:
        # Load existing conversation from the chat log
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Add the user's query to the message list
        messages.append({"role": "user", "content": f"{Query}"})
        
        # Call the Groq API with the full conversation and real-time info
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Specify the model to use
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,          # Limit the number of response tokens
            temperature=0.7,          # Controls creativity of the response
            top_p=1,
            stream=True,              # Enable streaming response
            stop=None
        )
        
        Answer = ""

        # Collect the streamed response
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # Remove unnecessary tokens from the response
        Answer = Answer.replace("</s>", "")

        # Append the assistant's response to the messages
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated conversation back to the file
        with open(r"Data\ChatLog.json", "w") as f: 
            dump(messages, f, indent=4)

        # Return the cleaned-up response
        return AnswerModifier(Answer=Answer)

    except Exception as e:
        # If there’s any error, print it and reset the chat log
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f: 
            dump([], f, indent=4)
        return ChatBot(Query)  # Retry the chatbot function

# Entry point: Run the chatbot in a loop for user input
if __name__ == "__main__":
    while True:
        user_input = input("Enter your Question: ") 
        print(ChatBot(user_input))
