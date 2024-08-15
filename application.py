from flask import Flask, render_template, request, redirect, url_for
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import os
import fitz

application = Flask(__name__)
app = application

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 500
        }

safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

model = genai.GenerativeModel(model_name = "models/gemini-pro",
                                   generation_config = generation_config,
                                   safety_settings = safety_settings)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/suggest-sentences', methods=['GET', 'POST'])
def suggest_sentences():
    if request.method == "POST":
        user_input = request.form['user_input_suggest']
        model_suggest = model.generate_content(f"Recommend for me a similar sentences through this sentence: {user_input}. Just only write the answer.")
        text_suggest = model_suggest.text
        return render_template('suggest.html', text_suggest=text_suggest)
    else:
        return render_template('suggest.html')

@app.route('/translation', methods=['GET', 'POST'])
def translation():
    if request.method == 'POST':
        if 'translation' not in request.files:
            return "No file part"
        file = request.files['translation']
        if file.filename == '':
            return "No selected file"
        if file and file.filename.endswith('.pdf'):
            pdf_content = extract_text_from_pdf(file)
            model_translation = model.generate_content(f"Screen this: {pdf_content}. Translate it to Vietnamese please. Just write the answer. Don't format anything. Capitalize the first letter of the word.")
            text_translation = model_translation.text
            return render_template('translation.html', text_translation=text_translation)
        if file and file.filename.endswith('.txt'):
            txt_content = extract_text_from_txt(file)
            model_translation = model.generate_content(f"Screen this resume: {txt_content}. Translate it to Vietnamese please. Just write the answer. Don't format anything. Capitalize the first letter of the word.")
            text_translation = model_translation.text
            return render_template('translation.html', text_translation=text_translation)
    return render_template('translation.html')
    
def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def extract_text_from_txt(txt_file):
    txt_file.seek(0)
    text = txt_file.read().decode('utf-8')
    return text


if __name__ == '__main__':
    app.run(debug=True)