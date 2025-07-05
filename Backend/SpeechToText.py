# Import necessary modules
from selenium import webdriver                                 # For browser automation
from selenium.webdriver.common.by import By                   # To locate HTML elements
from selenium.webdriver.chrome.service import Service          # For managing Chrome service
from selenium.webdriver.chrome.options import Options          # For setting Chrome options
from webdriver_manager.chrome import ChromeDriverManager       # Auto-installs the right ChromeDriver version
from dotenv import dotenv_values                               # Loads variables from .env file
import os                                                      # To interact with the OS (file paths)
import mtranslate as mt                                        # For automatic translation of text

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")  # Get the input language for speech recognition (e.g., 'en-US')

# HTML code with Web Speech API to recognize speech
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Inject the actual language code into the HTML JavaScript
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save the HTML code into a local file
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

# Get current working directory to construct absolute path to HTML file
current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"  # Path to local HTML file

# Set up Chrome options for Selenium
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")     # Skip permission popup for mic
chrome_options.add_argument("--use-fake-device-for-media-stream") # Use fake mic for testing
chrome_options.add_argument("--headless=new")                     # Run Chrome in headless mode

# Initialize the Chrome WebDriver with specified options
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define a temp path to store assistant status
TempDirPath = rf"{current_dir}/Frontend/Files"

# Function to set assistant status (e.g., “Listening”, “Translating”) in a file
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# Function to clean, format and punctuate user input
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()

    # List of question words to determine if sentence needs a question mark
    question_words = ["how", "what", "who", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]
    
    if any(word + " " in new_query for word in question_words):
        # Ensure it ends with a '?'
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Otherwise, end with a period '.'
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()  # Capitalize first letter

# Function to translate spoken text to English if not already in English
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Main function: Runs the speech recognition loop using the HTML page
def SpeechRecognition():
    driver.get("file:///" + Link)  # Load the local HTML page in browser
    driver.find_element(by=By.ID, value="start").click()  # Start listening

    while True:
        try:
            # Continuously check if any text is captured from the microphone
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:  # If speech is captured
                driver.find_element(by=By.ID, value="end").click()  # Stop recognition

                # Return either the original or translated text
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            pass  # Ignore exceptions (useful for looping while waiting for speech)

# If this file is run directly, keep listening and printing recognized speech
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
