import pandas as pd
import streamlit as st
from io import BytesIO
import re

@st.cache_data
def read_questions_from_excel(file_path):
    """
    Extracts numbered questions from an Excel file with 'Number' and 'Name' columns.
    
    Args:
        file_path (str): Path to the Excel file.
    
    Returns:
        List[str]: A list of questions in the format 'number question_text'.
    """
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    questions = []

    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        if 'Number' in df.columns and 'Name' in df.columns:
            for _, row in df.iterrows():
                number = str(row['Number']).strip()
                name = str(row['Name']).strip()
                questions.append(f"{number} {name}")
    
    return questions

def save_answers_to_excel(questions, answers):
    df = pd.DataFrame({"Question": questions, "Answer": answers})
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Q&A")
    output.seek(0)
    return output

