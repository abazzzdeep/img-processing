import cloudinary
import cloudinary.uploader
import tkinter as tk
from tkinter import filedialog, scrolledtext
import requests

# Configure Cloudinary
cloudinary.config(
    cloud_name="do5jb8irj",
    api_key="571294314387526",
    api_secret="DSmyvjXsRiHB4IYljKOOorV1fFU",  # Replace with your actual API secret
    secure=True
)

# Google Gemini API Key and URL
api_key = 'AIzaSyDzX-EtmogZAcM7s7NuucE3fvKjpkLuS2U'
api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'

def get_color_name_from_thecolorapi(hex_code):
    # Fetch color name from The Color API
    url = f"https://www.thecolorapi.com/id?hex={hex_code.strip('#')}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('name', {}).get('value', 'Unknown')
    else:
        return 'Unknown'

def generate_response(color_names):
    headers = {
        'Content-Type': 'application/json'
    }

    # Modify the prompt to suggest color combinations based on clothing colors
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Suggest stylish color combinations for clothing using the following colors: {', '.join(color_names)}."
                    }
                ]
            }
        ]
    }

    # Send the request to the Gemini API
    response = requests.post(api_url, headers=headers, json=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        try:
            # Adjusted to match the response structure
            return response_json['candidates'][0]['content']['parts'][0]['text'].strip()
        except KeyError as e:
            return f"Unexpected response structure: {e}"
    else:
        # Return an error message if the request failed
        return f"Error: {response.status_code} - {response.text}"

def upload_and_analyze_images(image_paths):
    color_names = []
    
    for image_path in image_paths:
        # Upload image to Cloudinary and extract dominant colors
        upload_result = cloudinary.uploader.upload(image_path, colors=True)
        
        # Extract the most dominant color hex code
        if "colors" in upload_result and upload_result["colors"]:
            hex_color = upload_result["colors"][0][0]  # First color hex (most dominant)
            color_name = get_color_name_from_thecolorapi(hex_color)  # Use The Color API
            color_names.append(color_name)
        else:
            color_names.append("Unknown")
    
    return color_names

def display_color_combinations():
    # Open file dialog to select images
    image_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    
    # Limit to 5 images
    if len(image_paths) > 5:
        text_area.config(state=tk.NORMAL)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "Please select up to 5 images only.")
        text_area.config(state=tk.DISABLED)
        return

    # Upload and analyze images to get color names
    color_names = upload_and_analyze_images(image_paths)
    
    # Create a custom prompt for Gemini
    custom_prompt = f"Suggest stylish color combinations for clothing using the following colors: {', '.join(color_names)}."
    
    # Generate response from Google Gemini
    suggestions = generate_response(color_names)
    
    # Display results in the text area
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, "Suggested Color Combinations:\n\n")
    text_area.insert(tk.END, suggestions)
    text_area.config(state=tk.DISABLED)

# Setting up the GUI window
window = tk.Tk()
window.title("Clothing Color Combination Suggestion")

# Label
label = tk.Label(window, text="Upload images of clothes for color combination suggestions:")
label.pack(pady=10)

# Button to upload images and get color combinations
button = tk.Button(window, text="Get Color Combinations", command=display_color_combinations)
button.pack(pady=10)

# ScrolledText widget to display the output
text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=70, height=15, state=tk.DISABLED)
text_area.pack(padx=10, pady=10)

# Running the GUI loop
window.mainloop()
