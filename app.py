import streamlit as st #For creating the web application
import google.generativeai as genai #For generating text using Googles's Generative AI
import os #For interacting with the os
import docx2txt #For extracting text from PDF files
import PyPDF2 as pdf #For extracting text from documents.
from dotenv import load_dotenv 

# Load environment variables from a .env file
load_dotenv()

# Configure the generative AI model with the Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Set up the model configuration for text generation
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Define safety settings for content generation
safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]


def generate_response_from_gemini(input_text):
     # Create a GenerativeModel instance with 'gemini-pro' as the model type
    llm = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
    )
    # Generate content based on the input text
    output = llm.generate_content(input_text)
    # Return the generated text
    return output.text

def extract_text_from_pdf_file(uploaded_file):
    # Use PdfReader to read the text content from a PDF file
    pdf_reader = pdf.PdfReader(uploaded_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += str(page.extract_text())
    return text_content

def extract_text_from_docx_file(uploaded_file):
    # Use docx2txt to extract text from a DOCX file
    return docx2txt.process(uploaded_file)

# Prompt Template
input_prompt_template = """
As an experienced Applicant Tracking System (ATS) analyst,
with profound knowledge in technology, software engineering, data science, business, 
and big data engineering, your role involves evaluating resumes against job descriptions.
Recognizing the competitive job market, provide top-notch assistance for resume improvement.
Your goal is to analyze the resume against the given job description, 
assign a percentage match based on key criteria, and pinpoint missing keywords accurately.
resume:{text}
description:{job_description}
I want the response in one single string having the structure
{{"Job Description Match":"%","Missing Keywords":"","Candidate Summary":"","Experience":""}}
"""

# Streamlit app
# Initialize Streamlit app
st.title("Intelligent ATS - Enhance Your Resume for ATS")
st.markdown('<style>h1{color: orange; text-align: center;}</style>', unsafe_allow_html=True)

# Input fields
job_description = st.text_area("Paste the Job Description", height=300)
uploaded_file = st.file_uploader("Upload Your Resume", type=["pdf", "docx"], help="Please upload a PDF or DOCX file")

# Submit button
submit_button = st.button("Submit")

if submit_button:
    if uploaded_file is not None:
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf_file(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx_file(uploaded_file)

        # Generate response using Gemini API
        response_text = generate_response_from_gemini(
            input_prompt_template.format(text=resume_text, job_description=job_description)
        )

        # Parse response to extract details
        import json
        response_data = json.loads(response_text)

        # Display the results in a cleaner format
        st.subheader("ATS Evaluation Result:")
        st.markdown(
            f"""
            - **Job Description Match:** {response_data.get("Job Description Match", "N/A")}
            - **Missing Keywords:** {response_data.get("Missing Keywords", "N/A")}
            - **Candidate Summary:** {response_data.get("Candidate Summary", "N/A")}
            - **Experience:** {response_data.get("Experience", "N/A")}
            """
        )

        # Display hiring recommendation
        match_percentage = float(response_data.get("Job Description Match", "0").replace('%', ''))
        if match_percentage >= 60:
            st.success("Recommendation: Move forward with hiring.")
        else:
            st.warning("Recommendation: Not a match.")
    else:
        st.error("Please upload a resume file to proceed.")
