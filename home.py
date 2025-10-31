import streamlit as st
from PIL import Image
import pdf2image
import pytesseract
import re
import pandas as pd
import cv2
import numpy as np
import cohere
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"



# Load environment variables

from dotenv import load_dotenv
import os
load_dotenv()

# Initialize Cohere client
cohere_api_key = os.getenv('COHERE_API_KEY')
co = cohere.Client(cohere_api_key)

# Function to get a response from the Cohere API

def get_chatbot_response(user_input):
    response = co.chat(
        model="command-r-plus-08-2024",  # ✅ Updated model
        message=user_input
    )
    return response.text

# Function to process and extract text from an uploaded file
def process_uploaded_file(uploaded_file):
    if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
        image = Image.open(uploaded_file)
        image = np.array(image)  # Convert to numpy array for OpenCV
        processed_image = preprocess_image(image)
        extracted_text = pytesseract.image_to_string(processed_image, config="--psm 6 --oem 3")
    else:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        extracted_text = ''
        for img in images:
            img_np = np.array(img)
            processed_image = preprocess_image(img_np)
            extracted_text += pytesseract.image_to_string(processed_image, config="--psm 6 --oem 3")
    return extracted_text

# Image Preprocessing function
def preprocess_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)
    denoised_image = cv2.GaussianBlur(thresh_image, (5, 5), 0)
    coords = np.column_stack(np.where(denoised_image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = denoised_image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed_image = cv2.warpAffine(denoised_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return deskewed_image

# Streamlit app setup
st.set_page_config(page_title="AI-Powered Disease Recognition", page_icon="🔬")
st.markdown("<h1 style='text-align: center; color: #4A90E2; margin-bottom: 10px;'>🔬 AI-Powered Disease Recognition</h1>", unsafe_allow_html=True)

st.write("### Upload your Blood Report (Image) for analysis:")
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded successfully! Processing... 🕵️‍♂️")
    extracted_text = process_uploaded_file(uploaded_file)

    patterns = {
        "Patient Name": r"Patient Name\s*=\s*[:=]?\s*(.*?)(?:\s*Date|$)",
        "Age": r"Age/Gender\s*:\s*(\d+)\s*Years\s*/\s*(Male|Female)",
        "Sex": r"Age/Gender\s*:\s*\d+\s*Years\s*/\s*(Male|Female)",
        "Hemoglobin": r"HAEMOGLOBIN\s*(\d+\.\d+|\d+)\s*gm%",
        "RBC Count": r"R\.B\.C\.Count\s*(\d+\.\d+|\d+)\s*mill/emm",
        "PCV": r"P\.C\.V\.\s*(\d+\.\d+|\d+)\s*%\s*",
        "MCV": r"Mean Corpuscular Volume \(MCV\)\s*(\d+\.?\d*)\s*fL",
        "MCH": r"M\.C\.H\.\s*(\d+\.\d+|\d+)\s*pg",
        "MCHC": r"M\.C\.H\.C\.\s*(\d+\.\d+|\d+)\s*%",
        "RDW": r"R\.D\.W\.\s*(\d+\.\d+|\d+)\s*cv%",
        "Total WBC Count": r"Total\s*WBC\s*count\s*(\d+)\s*|W\.B\.C\.Count\s*(\d+)\s*/cumm",
        "Neutrophils": r"Neutrophils\s*(\d+)\s*%",
        "Lymphocytes": r"Lymphocytes\s*(\d+)\s*%",
        "Eosinophils": r"Eosinophils\s*(\d+)\s*%",
        "Monocytes": r"Monocytes\s*(\d+)\s*%",
        "Basophils": r"Basophils\s*(\d+)\s*%",
        "ESR": r"ESR\s*(\d+)\s*",
        "Platelet Count": r"Platelet Count\s*(\d+)\s*/cumm",
    }

    units = {
        "Patient Name": "",
        "Age": "Years",
        "Sex": "",
        "Hemoglobin": "g/dL",
        "RBC Count": "million/µL",
        "PCV": "%",
        "MCV": "fL",
        "MCH": "pg",
        "MCHC": "g/dL",
        "RDW": "%",
        "Total WBC Count": "thousand/µL",
        "Neutrophils": "cells/µL",
        "Lymphocytes": "cells/µL",
        "Eosinophils": "cells/µL",
        "Monocytes": "cells/µL",
        "Basophils": "cells/µL",
        "ESR": "mm/hr",
        "Platelet Count": "thousand/µL",
    }

    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            extracted_value = match.group(1) if match.group(1) else match.group(2)
            extracted_data[key] = f"{extracted_value} {units[key]}"

    if extracted_data:
        df = pd.DataFrame.from_dict(extracted_data, orient='index', columns=['Value'])

        user_input = ', '.join([f"{key}: {extracted_data[key]}" for key in extracted_data.keys()])
        diagnosis = get_chatbot_response(f"Based on the following blood report data: {user_input}, what possible diseases could be indicated?")

        st.subheader("🩺 Diagnosis")
        st.write(diagnosis)

        df.to_excel("extracted_data.xlsx", index=False)
        st.success("📋 Extracted data has been saved to 'extracted_data.xlsx'.")
    else:
        st.warning("❌ No relevant data was found in the uploaded document.")

# Chatbot functionality with session state to store conversation history
st.markdown("<div class='chat-section' style='margin-top: 20px; padding: 1rem; border-radius: 8px; background-color: #f8f8f8;'><h3 style='color: #4A90E2; margin-top: 10px; margin-bottom: 5px;'>🤖 Chat with the Bot</h3></div>", unsafe_allow_html=True)
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

user_message = st.text_input("💬 Ask a question about the blood report:")

if st.button("Send"):
    if user_message:
        context = f"Here is the extracted data: {user_input}. Previous conversation: " + " ".join(st.session_state['chat_history'])
        response = get_chatbot_response(context + " " + user_message)

        st.session_state['chat_history'].append(f"User: {user_message}")
        st.session_state['chat_history'].append(f"Bot: {response}")

        for chat in st.session_state['chat_history']:
            if chat.startswith("User:"):
                st.markdown(f"<div style='background-color: #d1e7dd; border-radius: 5px; padding: 0.5em; margin: 0.5em 0;'>{chat}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color: #ffeeba; border-radius: 5px; padding: 0.5em; margin: 0.5em 0;'>{chat}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter a message.")
