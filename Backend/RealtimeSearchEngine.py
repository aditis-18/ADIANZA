# Import required libraries
from googlesearch import search             # For performing Google searches
from groq import Groq                       # For accessing the Groq API (likely using LLaMA models)
from json import load, dump                 # For reading and writing JSON files
import datetime                             # For accessing current date and time
from dotenv import dotenv_values            # For loading environment variables from .env file

# Load environment variables
env_vars = dotenv_values(".env")

# Get specific variables from the environment
Username = env_vars.get("Username")              # Your username
Assistantname = env_vars.get("Assistantname")    # Assistant's name
GroqAPIKey = env_vars.get("GroqAPIKey")          # API Key for Groq

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System message to define assistant behavior and personality
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try loading previous chat history from a JSON file
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)  # Load existing messages if file exists
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)  # If file doesn't exist, create a new one with an empty list

# Function to perform a Google search and return the top 5 results
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))  # Get top 5 search results
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        # Format each result with title and description
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"  # Mark end of results
    print(Answer)
    return Answer  # Return formatted search results

# Function to clean up the assistant's final response by removing extra blank lines
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = {line for line in lines if line.strip()}  # Remove empty lines
    modified_answer = '\n'.join(non_empty_lines)  # Join cleaned lines
    return modified_answer

# Starting message history with system and greeting messages
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "HI"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to generate real-time information like current day, time, date, etc.
def Information():
    data = "" 
    current_date_time = datetime.datetime.now()  # Get current datetime
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")    
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    # Construct a formatted string with all time info
    data = f"Please use this real-time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours: {minute} minutes: {second} seconds.\n"
    return data

# Main function to generate a response using real-time data + Google search + LLM
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages  # Use global message history

    # Load chat log from file again for updated history
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    # Add user's new prompt to the conversation
    messages.append({"role": "user", "content": f"{prompt}"})

    # Perform Google search and add results to system prompt
    SystemChatBot.append({"role": "user", "content": GoogleSearch(prompt)})

    # Make a streaming request to the LLaMA 3 model via Groq
    completion = client.chat.completions.create(
        model="llama3-70b-8192",  # Specify the model
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        max_tokens=2048,          # Limit the size of the response
        temperature=0.7,          # Response creativity
        top_p=1,                  # Top-p sampling
        stream=True,              # Enable streaming response
        stop=None
    )

    Answer = ""  # Initialize empty string to collect response

    # Read streaming response from the model
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content  # Append each part to the answer

    # Clean up the generated response
    Answer = Answer.strip().replace("</s>", "")
    
    # Save assistant's response to message history
    messages.append({"role": "assistant", "content": Answer})

    # Save updated chat history to JSON file
    with open(r"Data\ChatLog.json", "w") as f: 
        dump(messages, f, indent=4)

    # Remove last Google search entry from SystemChatBot to avoid buildup
    SystemChatBot.pop()

    # Return cleaned-up answer
    return AnswerModifier(Answer=Answer)

# If script is run directly, enter interactive mode
if __name__ == "__main__":
    while True:
        prompt = input("Enter your Query: ")  # Get user input
        print(RealtimeSearchEngine(prompt))   # Process and display result
