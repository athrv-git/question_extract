import streamlit as st
from utils.file_handler import read_questions_from_excel, save_answers_to_excel
from utils.api_client import generate_answer_from_api

st.set_page_config(page_title="Excel Q&A App", layout="wide")
st.title("📄 Excel-Based Question Answer Form")

# -----------------------------
# Sidebar Chatbot
# -----------------------------
with st.sidebar:
    st.header("💬 Chatbot")

    # init chat history
    if "chat" not in st.session_state:
        st.session_state.chat = []  # list of {"role": "user"|"assistant", "content": str}
    if "sidebar_input" not in st.session_state:
        st.session_state.sidebar_input = ""

    # show chat history
    chat_box = st.container()
    if st.session_state.chat:
        for msg in st.session_state.chat:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Assistant:** {msg['content']}")
    else:
        st.caption("Start a conversation below!")

    # input + actions
    st.session_state.sidebar_input = st.text_area(
        "Type your question",
        value=st.session_state.sidebar_input,
        height=80,
        label_visibility="collapsed",
        key="sidebar_textarea",
        placeholder="Ask anything…"
    )

    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        send_clicked = st.button("Send", key="sidebar_send_btn")
    with col_sb2:
        clear_clicked = st.button("Clear", key="sidebar_clear_btn")

    if clear_clicked:
        st.session_state.chat = []
        st.session_state.sidebar_input = ""
        st.rerun()

    if send_clicked and st.session_state.sidebar_input.strip():
        user_prompt = st.session_state.sidebar_input.strip()
        st.session_state.chat.append({"role": "user", "content": user_prompt})
        with st.spinner("Thinking…"):
            try:
                reply = generate_answer_from_api(user_prompt)
            except Exception as e:
                reply = f"Oops, I couldn't get an answer right now: {e}"
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.session_state.sidebar_input = ""  # clear input after send
        st.rerun()

# -----------------------------
# Column Name Configuration
# -----------------------------
st.markdown("### ⚙️ Excel Column Configuration")
st.markdown("Specify the column names in your Excel file:")

col_config1, col_config2 = st.columns(2)
with col_config1:
    question_column = st.text_input(
        "Question Number Column",
        value="Number",
        help="Enter the name of the column containing question numbers/IDs"
    )
with col_config2:
    answer_column = st.text_input(
        "Question Text Column",
        value="Name",
        help="Enter the name of the column containing question text"
    )

st.markdown("---")

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload an Excel file (.xlsx) with questions",
    type=["xlsx"]
)

if uploaded_file:
    try:
        questions = read_questions_from_excel(
            uploaded_file, 
            question_col=question_column, 
            answer_col=answer_column
        )

        if not questions:
            st.warning(f"No questions found using columns '{question_column}' and '{answer_column}'. Please check your column names.")
        else:
            st.success(f"{len(questions)} questions loaded.")

            if "answers" not in st.session_state or len(st.session_state.answers) != len(questions):
                st.session_state.answers = [""] * len(questions)

            st.markdown("### ✏️ Answer the following questions:")

            for idx, question in enumerate(questions):
                with st.container():
                    col1, col2, col3 = st.columns([1.5, 3, 0.5])
                    with col1:
                        st.markdown(f"**Q{idx+1}. {question}**")
                    with col2:
                        st.session_state.answers[idx] = st.text_area(
                            label=f"Answer {idx+1}",
                            value=st.session_state.answers[idx],
                            key=f"answer_{idx}",
                            label_visibility="collapsed",
                            height=80
                        )
                    with col3:
                        if st.button("✨", key=f"gen_btn_{idx}"):
                            with st.spinner(f"Generating answer for Q{idx+1}..."):
                                generated = generate_answer_from_api(question)
                                st.session_state.answers[idx] = generated
                                st.rerun()


            st.markdown("---")
            col_btn1, col_btn2 = st.columns([1, 3])
            with col_btn1:
                if st.button("🚀 Generate All Answers", type="primary"):
                    with st.spinner("Generating answers for all questions..."):
                        for idx, question in enumerate(questions):
                            generated = generate_answer_from_api(question)
                            st.session_state.answers[idx] = generated
                        st.success("✅ All answers generated!")

            st.markdown("---")
            st.subheader("📥 Download your answers")
            excel_file = save_answers_to_excel(questions, st.session_state.answers)

            st.download_button(
                label="📄 Download Q&A Excel",
                data=excel_file,
                file_name="answered_questions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")