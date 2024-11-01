import streamlit as st
__import__('pysqlite3') 
import sys 
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3') 
# from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import pandas as pd
import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup



def create_streamlit_app(llm, profiles, clean_text):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a URL:")
    submit_button = st.button("Submit")

    if submit_button:
        try:

            
            response = requests.get(url_input)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html")
            text = soup.body.get_text(separator="\n", strip=True)
            # loader = WebBaseLoader([url_input])
            data = clean_text(text)
            profiles.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = profiles.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


rad = st.sidebar.radio("Navigation",["Home","Generator","Sender","Database"])
if rad == "Home":
    st.title("🤖 Cold Email Generator & Sender")
    st.subheader("About:")
    st.write("Generate high-quality, personalized cold emails with AI in seconds! Our AI-Powered Cold Email Generator & Sender is designed to help you reach out with impact. Whether you are connecting with potential employers, clients, or networking opportunities, this tool crafts emails tailored to your recipients needs and your unique goals. Simply input a website link that contains a job posting you want to apply and let the AI create a compelling, polished message that stands out in any inbox.It also includes all eligible Students List into the Email. With automated sending options, and privacy-focused design, your outreach is just a click away. Connect smarter and more efficiently with AI-driven emails that make the right impression every time.This website is particulary designed for Placement Incharge for Bharat Institute of Engineering and Technology.")
    st.subheader("How to use:")
    st.write("1. Enter a website a link that contains job posting into the Generator and click Submit.")
    st.write("2. This will create a Cold Email , Click on copy option on top right corner.")
    st.write("3. Open Sender page and paste the copied email and fill the remaining details.")
    st.write("4. Watch this video to find the app password")
    st.video("C:/Users/ronit/OneDrive/Desktop/try/app/Password finder.mp4")
    st.write("5. The Email will be sent successfully.")
    st.write("6. To see the student details open Database webpage.")
    st.subheader("Key Benefits:")
    st.write("1. Saves a lot of time, Generate and send Cold Email in Seconds.")
    st.write("2. Tailored to Each Recipient , generates on specific job roles.")
    st.write("3. Increased response rates")
    st.write("4. Consistency, Reliability and Security")
    st.subheader("Note:")
    st.write(" This Cold Email Generator is designed to be used specifically by Placements Incharge of Bharat Institute of Engineering and Technology, the database is original students profiles, Donot misuse this project. ")
if rad == "Generator": 
    # st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    
    chain = Chain()
    profiles = Portfolio()
    # st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, profiles, clean_text)
    # st.title("Cold Email Generator")

if rad == "Sender":
    if "from_email" not in st.session_state:
        st.session_state.from_email = ""
        st.session_state.password = ""
        st.session_state.to_email = ""
        st.session_state.subject = ""
        st.session_state.body = ""




    st.title("📨 Email Sender")

    # Input fields
    st.session_state.from_email = st.text_input("From (your email)",st.session_state.from_email)
    st.session_state.password = st.text_input("Password", type="password",value=st.session_state.password)
    to_email = st.text_input("To (recipient's email)")
    subject = st.text_input("Subject")
    body = st.text_area("Body",height=500)

    if st.button("Send Email"):

        if st.session_state.from_email and st.session_state.password and to_email and subject and body:
            try:

                progress = st.progress(0)
                # Set up the MIME
                msg = MIMEMultipart()
                msg['From'] = st.session_state.from_email
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                progress.progress(20)

                # Create SMTP session
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    progress.progress(40)
                    server.login(st.session_state.from_email, st.session_state.password)
                    progress.progress(60)
                    server.sendmail(st.session_state.from_email, to_email, msg.as_string())
                    progress.progress(80)

                progress.progress(100)

                st.success("Email sent successfully!")
                progress.empty()
            except Exception as e:
                st.error(f"Error: {e}")
                progress.empty()
        else:
            st.warning("Please fill in all fields.")


if rad == "Database":
    st.title("Students data")
    data=pd.read_csv("C:/Users/ronit/OneDrive/Desktop/minor_project/minipro/app/resource/Student_profiles.csv")
    st.table(data)


