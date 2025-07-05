# Import required modules
import asyncio                           # For asynchronous operations
from random import randint              # To generate random seed values for image generation
from PIL import Image                   # To open and display images
import requests                         # For sending HTTP requests
from dotenv import get_key              # To securely get API key from .env file
import os                               # For handling file paths
from time import sleep                  # For adding delay/sleep in loops

# Function to open and display all generated images based on the prompt
def open_image(prompt):
    folder_path = r"Data"                             # Path to the folder containing images
    prompt = prompt.replace(" ", "_")                 # Replace spaces in prompt for filename compatibility

    # Prepare a list of expected image filenames (prompt1.jpg to prompt4.jpg)
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    # Loop through each image file and attempt to open and show it
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)              # Open image file
            print(f"opening image: {image_path}")     # Print which image is being opened
            img.show()                                # Display the image
            sleep(1)                                   # Small delay to allow image to open
        except IOError:
            print(f"Unable to open {image_path}")     # Handle case where file doesn't exist or fails to open

# Set the HuggingFace model endpoint URL
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Retrieve API key from .env file and prepare headers
headers = {
    "Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"
}

# Asynchronous function to send the request to the model API
async def query(payload):
    # Run the HTTP request in a separate thread to avoid blocking
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content                              # Return the raw image content

# Asynchronous function to generate 4 images based on the prompt
async def generate_images(prompt: str):
    tasks = []                                           # List to store all async tasks

    for _ in range(4):                                   # Generate 4 images
        # Add more detailed and high-quality image instructions to the prompt
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))         
      # Create async task for image generation
        tasks.append(task)                               # Add the task to the list

    # Wait for all image generation tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Save each generated image to the Data folder
    for i, image_bytes in enumerate(image_bytes_list):
        with open(f"Data/{prompt.replace(' ', '_')}{i+1}.jpg", "wb") as f:
            f.write(image_bytes)                         # Write image content to file

# Synchronous wrapper function to call the async image generation and then display the images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))                # Run the async image generation
    open_image(prompt)                                   # Open and show the images

# Main loop to monitor the ImageGeneration.data file for trigger
while True:
    try:
        # Open the control file and read the prompt and status
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()

        # Split the data into Prompt and Status
        Prompt, Status = [x.strip() for x in Data.split(",")]

        # If the status is "True", begin image generation
        if Status == "True":
            print("GeneratingImages...")
            ImageStatus = GenerateImages(prompt=Prompt)  # Call the image generation function

            # After image generation, reset the status flags in the control file
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False, False")
                break                                     # Exit the loop after generating images
        else:
            sleep(1)                                      # Wait for 1 second before checking again
    except:
        pass                #Silently ignore any exceptions (not recommended in production)
