# Importing required libraries and modules
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")

# CSS classes possibly used in Google for search parsing
classes = [
    "zCubwf", "hgKElc", "LTLOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d",
    "webanswers-webanswers_table__webanswers-table", "dDoNo iKb4Bb gsrt", "sXLaOe",
    "LWKfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

# Custom user-agent
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Context for chat
messages = []

# System message prompt
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {Username}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."
}]

# Function to perform Google Search
def GoogleSearch(Topic):
    search(Topic)
    return True

# Function to generate content and open it in Notepad
def Content(Topic):
    import traceback

    def OpenNotepad(File):
        try:
            full_path = os.path.abspath(File)
            print(f"[INFO] Opening Notepad with file: {full_path}")
            if not os.path.exists(full_path):
                print(f"[ERROR] File does not exist: {full_path}")
                return
            subprocess.Popen(["notepad.exe", full_path])
        except Exception as e:
            print(f"[ERROR] Could not open Notepad: {e}")

    def ContentWriterAI(prompt):
        try:
            messages.append({"role": "user", "content": f"{prompt}"})
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )
            Answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content
            Answer = Answer.replace("</s>", "")
            messages.append({"role": "assistant", "content": Answer})
            return Answer.strip()
        except Exception as e:
            print("[ERROR] Groq API error:")
            traceback.print_exc()
            return ""

    # Clean Topic
    Topic = Topic.replace("content ", "").strip()
    ContentByAI = ContentWriterAI(Topic)

    if not ContentByAI:
        print("[ERROR] No content generated. Skipping file creation.")
        return False

    print("[DEBUG] Content generated:\n", ContentByAI)

    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{Topic.lower().replace(' ', '')}.txt")

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ContentByAI)
            print("[DEBUG] Content written to file successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to write content to file: {e}")
        return False

    OpenNotepad(file_path)
    return True

# Function to search on YouTube
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Function to play a video directly
def PlayYouTube(query):
    playonyt(query)
    return True

# Function to open applications or fallback to web
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[AppOpener error]: {e}")

        manual_apps = {
            "linkedin": "https://www.linkedin.com",
            "instagram": "https://www.instagram.com"
        }

        app_lower = app.strip().lower()
        if app_lower in manual_apps:
            print(f"[INFO] Opening in browser: {manual_apps[app_lower]}")
            webopen(manual_apps[app_lower])
            return True

        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links if link.get('href')]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        links = extract_links(html)

        if links:
            webopen(links[0])
        else:
            print(f"[ERROR] No usable link found for '{app}'.")

        return True

# Function to close apps
def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

# Function to control system volume
def System(command):
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume unmute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    if command == "mute": mute()
    elif command == "unmute": unmute()
    elif command == "volume up": volume_up()
    elif command == "volume down": volume_down()

    return True

# Translate and execute commands asynchronously
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            if "open it" in command or "open file" == command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"[WARN] No function found for command: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Master automation function
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

# Entry point
if __name__ == "__main__":
    # Example: play song, open apps, generate content
    asyncio.run(Automation([
        "open Instagram",
        "open LinkedIn",
        "play Tum Se",
        "content sick leave application"
    ]))
