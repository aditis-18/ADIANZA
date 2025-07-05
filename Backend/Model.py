# Import required libraries
import cohere                       # Cohere's SDK for accessing its language models
from rich import print              # For better console output formatting
from dotenv import dotenv_values    # For loading environment variables from a .env file

# Load all environment variables from the .env file
env_vars = dotenv_values(".env")

# Retrieve the Cohere API key from the environment variables
CohereAPIKey = env_vars.get("CohereAPIKey")

# Initialize Cohere client using the API key
co = cohere.Client(api_key=CohereAPIKey)

# List of function keywords that the decision-making model can detect
funcs = [
    "exit", "general", "realtime", "open", "close", "play", 
    "generate image", "system", "content", "google search", 
    "youtube search", "reminder"
]

# List to store messages in the current session (not used in logic but declared for extensibility)
messages = []

# Detailed preamble that guides the language model on how to classify user queries
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation...

[TRUNCATED FOR BREVITY: same preamble as in your original code. It's a full instruction set explaining when to respond with each function type like 'open', 'play', 'realtime', etc.]

*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Predefined chat history to fine-tune the decision-making behavior of the model
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date by the way remind me that I have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

# Function to decide the type of query using Cohere's chat model
def FirstLayerDMM(prompt: str = "test"):

    # Append the user's input to the messages list (for potential future use)
    messages.append({"role": "user", "content": f"{prompt}"})

    # Start a streaming chat with Cohere using the specified preamble and chat history
    stream = co.chat_stream(
        model='command-r-plus',           # Use command-r-plus model
        message=prompt,                   # User's current input
        temperature=0.7,                  # Response creativity level
        chat_history=ChatHistory,         # Contextual chat history to help model classify better
        prompt_truncation='OFF',          # Prevent truncation of prompt
        connectors=[],                    # No external connectors
        preamble=preamble                # Instructional guide for the model
    )

    response = " "                        # Empty response buffer

    # Read the stream from Cohere as it's generated
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text       # Accumulate text content from stream

    # Clean up the generated response
    response = response.replace("\n", "")        # Remove newline characters
    response = response.split(",")               # Split response by comma (handles multiple actions)
    response = [i.strip() for i in response]     # Trim whitespace

    temp = []                            # List to store filtered valid function outputs

    # Filter and keep only known function-prefixed responses
    for task in response:
        for func in funcs:
             if task.startswith(func):
                 temp.append(task)

    response = temp                      # Update response with only valid detected actions

    # If the model responded generically (e.g., 'general (query)'), re-run classification
    if "(query)" in response:
         newresponse = FirstLayerDMM(prompt=prompt)
         return newresponse
    else:
         return response                 # Return final list of valid command classifications

# If run directly as a script, enter loop for continuous input
if __name__ ==  "__main__":

    while True:
        print(FirstLayerDMM(input(">>> ")))      # Prompt user for input and print model's decision
