# AI-Powered Disease Recognition

This Streamlit application analyzes blood report images and provides possible diagnoses based on the extracted data. It utilizes OCR (Optical Character Recognition) to extract information from images and a chatbot powered by Cohere's API for interactive user queries.

## Features

- Upload blood report images in PNG or JPEG format.
- Automatic extraction of key medical values from the reports.
- Interactive chatbot that provides possible disease diagnoses based on extracted data.
- Downloadable Excel file containing the extracted data.

## Requirements

To run this application, you will need the following packages:

- `streamlit`
- `PIL` (Pillow)
- `pdf2image`
- `pytesseract`
- `opencv-python`
- `numpy`
- `pandas`
- `cohere`
- `python-dotenv`

You can install the required packages using pip:

```bash
pip install streamlit Pillow pdf2image pytesseract opencv-python numpy pandas cohere python-dotenv
