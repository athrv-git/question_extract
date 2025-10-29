import pandas as pd
import streamlit as st
from io import BytesIO
import re

@st.cache_data
def read_questions_from_excel(file_path, question_col='Number', answer_col='Name'):
    """
    Extracts questions from an Excel file using specified column names.
    
    Args:
        file_path (str): Path to the Excel file.
        question_col (str): Name of the column containing question numbers/IDs.
        answer_col (str): Name of the column containing question text.
    
    Returns:
        List[str]: A list of questions in the format 'question_number question_text'.
    """
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    questions = []

    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        if question_col in df.columns and answer_col in df.columns:
            for _, row in df.iterrows():
                number = str(row[question_col]).strip()
                name = str(row[answer_col]).strip()
                questions.append(f"{number} {name}")
    
    return questions

def save_answers_to_excel(questions, answers):
    df = pd.DataFrame({"Question": questions, "Answer": answers})
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Q&A")
    output.seek(0)
    return output