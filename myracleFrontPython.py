from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
from PIL import Image
from werkzeug.utils import secure_filename
import os

# Initialize the Flask app
app = Flask(__name__)
CORS(app) 
# Set the API key directly
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Define the upload folder
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']

    if image_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    option_text = request.form.get('option', '')
    print("additional texts: " + option_text)
    # Save the uploaded image to the 'uploads' folder
    filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)

    # Open the image using PIL
    img = Image.open(image_path)
    prompt = f"""
    Output should describe a detailed, step-by-step guide on how to test each functionality. Each test case should include:
    - Description: What the test case is about.
    - Pre-conditions: What needs to be set up or ensured before testing(Clearly explain in 2-4 lines ).
    - Testing Steps: Clear, step-by-step instructions on how to perform the test(Explore all possible condition behave like a real production tester).
    - Expected Result: What should happen if the feature works correctly.

    If there are multiple functionalities, list each functionality as a heading and define the above for each.

    Additional Context:
    {option_text}
    """
    # Interact with the Google Generative AI model
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content([prompt, img])
        print(jsonify({'generated_text': response.text}))
        # Return the generated text from the LLM
        return jsonify({'generated_text': response.text}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
