from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub

# Load environment variables
load_dotenv()

# Configure Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Streamlit App Configuration
st.set_page_config(page_title="Multi-Function App")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Text to SQL", "Ask Your PDF"])

# Text to SQL Functionality
def text_to_sql():
    st.header("Gemini App To Retrieve SQL Data")
    
    # Get the database file from the user
    uploaded_file = st.file_uploader("Choose a database file", type=['db'])
    
    # Get table name and column names from the user
    table_name = st.text_input("Enter the table name", key="columns")
    col_names = st.text_area("Column names", key="col_names")
    
    # Define the prompt
    prompt = [
        f"""
        You are an expert in converting English questions to SQL query!
        The SQL database has the name {table_name} and has the following columns - {col_names}
        \n\nSuppose there is a table named {table_name} , let me explain how you will convert the text to SQL:
        \nExample 1 - How many entries of records are present?, 
        the SQL command will be something like this: SELECT COUNT(*) FROM {table_name};
        \nExample 2 - Tell me all the students studying in Data Science class?, 
        the SQL command will be something like this: SELECT * FROM {table_name} 
        WHERE CLASS='Data Science'; 
        The SQL code should not have ``` at the beginning or end and should not contain the word 'sql'.
        """
    ]
    
    # Save the uploaded database file
    def save_uploaded_file(uploaded_file):
        temp_file_path = "uploaded_database.db"
        with open(temp_file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        return temp_file_path
    
    # Load the database
    if uploaded_file is not None:
        db_path = save_uploaded_file(uploaded_file)
    
        # Ask a question and convert it to SQL
        question = st.text_input("Write your question here", key="input")
        submit = st.button("Convert")
    
        # If submit is clicked
        if submit:
            try:
                response = get_gemini_response(question, prompt)
                st.write(f"Generated SQL Query: {response}")
    
                # Read the query result from the database
                query_result = read_sql_query(response, db_path)
                st.write("Query Results:")
                for row in query_result:
                    st.write(row)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.write("Please upload a database file to proceed.")

# PDF Chat Functionality
def ask_your_pdf():
    st.header("Ask Your PDF")
    
    pdf = st.file_uploader("Upload your pdf", type="pdf")
    
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    
        # Split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
    
        # Create embedding
        embeddings = HuggingFaceEmbeddings()
    
        knowledge_base = FAISS.from_texts(chunks, embeddings)
        token = "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"
        user_question = st.text_input("Ask Question about your PDF:")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)
            llm = HuggingFaceHub(
                repo_id="google/flan-t5-large",
                model_kwargs={"temperature": 0.7, "max_length": 64},
                huggingfacehub_api_token=token)
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=user_question)
    
            st.write(response)

# Define the prompt for text to SQL
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to retrieve query from the database
def read_sql_query(sql, db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows

# Render the selected page
if page == "Text to SQL":
    text_to_sql()
elif page == "Ask Your PDF":
    ask_your_pdf()
