# Import necessary modules
import pygame                         # For playing audio
import random                         # To pick random responses
import asyncio                        # To handle async audio generation
import edge_tts                       # Microsoft's Edge TTS for realistic voices
import os                             # For file handling
from dotenv import dotenv_values      # For reading environment variables from .env

# Load environment variable for voice configuration
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")  # Example: "en-US-GuyNeural"

# Async function to convert text to audio and save it as a file
async def TextToAudioFile(text) -> None:
    file_path = r"Data\Speech.mp3"

    # If file already exists, remove it to avoid conflicts
    if os.path.exists(file_path):
        os.remove(file_path)

    # Initialize the Edge TTS client with voice, pitch, and rate settings
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')

    # Save the synthesized speech as an MP3 file
    await communicate.save(file_path)

# Function to play the generated speech audio
# `func` is an optional callback to control playback interruption
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Run the async audio generation function
            asyncio.run(TextToAudioFile(Text))

            # Initialize the Pygame mixer
            pygame.mixer.init()

            # Load and play the speech audio
            pygame.mixer.music.load(r"Data\Speech.mp3")
            pygame.mixer.music.play()

            # Monitor playback; allows early termination if func() returns False
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)  # Avoid CPU overuse

            return True  # Playback completed

        except Exception as e:
            print(f"Error in TTS: {e}")  # Print any TTS error

        finally:
            try:
                # Call func with False when ending playback
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in finally block: {e}")  # Final block error

# Main Text-to-Speech dispatcher with smart handling for long texts
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")  # Split the input by periods to check length

    # Possible polite system messages for long responses
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
   
    # If the text is long enough, read only the first 2 sentences + a polite redirection
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)  # Otherwise, read the full text

# Main execution loop: repeatedly ask for input and read it out
if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the Text:"))
