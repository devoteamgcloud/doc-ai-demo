import streamlit as st 
from PIL import Image, ImageOps, ImageDraw

from openai import OpenAI # for calling the OpenAI API


from google.api_core.client_options import ClientOptions
from google.cloud import documentai

import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('path to env file')
load_dotenv(dotenv_path=dotenv_path)

#envs
PROJECT_ID = os.getenv('PROJECT_ID') # project id of gcp project with processor
LOCATION = os.getenv('LOCATION')  # Format is 'us' or 'eu'
PROCESSOR_ID = os.getenv('PROCESSOR_ID')  # Create processor in Cloud Console: Document AI -> My Processors -> create custom processor
PICTURE = os.getenv('PICTURE')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL') # for example text-embedding-ada-002
GPT_MODEL = os.getenv('GPT_MODEL') # for example gpt-3.5-turbo
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

#MIME_TYPE = "image/jpeg"

def draw_boxes(image, bounds, color):
    """Draws a border around the image using the hints in the vector list.

    Args:
        image: the input image object.
        bounds: list of coordinates for the boxes.
        color: the color of the box.

    Returns:
        An image with colored bounds added.
    """
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon(
            [
                bound.vertices[0].x,
                bound.vertices[0].y,
                bound.vertices[1].x,
                bound.vertices[1].y,
                bound.vertices[2].x,
                bound.vertices[2].y,
                bound.vertices[3].x,
                bound.vertices[3].y,
            ],
            None,
            color,
            width=2,
        )
    return image



# Instantiates a client
docai_client = documentai.DocumentProcessorServiceClient(
    client_options=ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
)

# The full resource name of the processor, e.g.:
# projects/project-id/locations/location/processor/processor-id
# You must create new processors in the Cloud Console first
name = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
OPENAI_API_KEY = "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"

openai = OpenAI(
  api_key = OPENAI_API_KEY,  # this is also the default, it can be omitted
)


st.set_page_config(
    page_title="Email classification",
    page_icon = ":mailbox_with_mail:",
    initial_sidebar_state = 'auto'
)

# hide_streamlit_style = """
# 	<style>
#   #MainMenu {visibility: hidden;}
# 	footer {visibility: hidden;}
#   </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .small-font {
        font-size:12px;
        font-style: italic;
        color: #b1a7a6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



with st.sidebar:
        st.image(PICTURE)
        st.title("Email recognition")
        st.subheader("Providing multiple functionalities to process and anlyze physical letters, such as text detection, summarization, recipient detection ... ")

st.write("""
         # Mail Detection App
         """
         )


file = st.file_uploader("", type=["jpg", "png"])
#slider_val = st.slider("Temperature", 0.0, 1.0, 0.1)
checkbox_summary = st.checkbox("Summary", value=True)
checkbox_recipient = st.checkbox("Mail recipient", value=True)
checkbox_ocr = st.checkbox("Letter detection", value=True)
checkbox_sensitive = st.checkbox("Detect sensitive information", value=True)

# Every form must have a submit button.
submitted = st.button("Submit")

if file is None:
    st.text("Please upload an image file")
else:
    if submitted:
        FILE_PATH = file.name
        if FILE_PATH.lower().endswith("jpg"):
            MIME_TYPE = "image/jpeg"
        elif FILE_PATH.lower().endswith("png"):
            MIME_TYPE = "image/png"
        image = Image.open(file)
        st.image(image, use_column_width=True)

        image_content = file.getvalue()
        raw_document = documentai.RawDocument(content=image_content, mime_type=MIME_TYPE)

        # Configure the process request
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        # Use the Document AI client to process the sample form
        result = docai_client.process_document(request=request)
        document_object = result.document
        print("Document processing complete.")

        query = f"""Use the below letter  to answer the subsequent question. If the answer cannot be found, write "I don't know."

        Letter:
        \"\"\"
        {document_object.text}
        \"\"\"

        Question: Who is the recipient of the email? Answer only by giving first and last name, without an introduction phrase"""

        response = openai.chat.completions.create(
            messages=[
                {'role': 'system', 'content': 'You answer regarding the recipient of the email.'},
                {'role': 'user', 'content': query},
            ],
            model=GPT_MODEL,
            temperature=0,
        )

        query1 = f"""Use the below letter  to do a summary of the letter. If the answer cannot be found, write "I don't know."

        Letter:
        \"\"\"
        {document_object.text}
        \"\"\""""

        response1 = openai.chat.completions.create(
            messages=[
                {'role': 'system', 'content': 'You answer regarding the summary of the email.'},
                {'role': 'user', 'content': query1},
            ],
            model=GPT_MODEL,
            temperature=0,
        )

        query2 = f"""Use the below letter  to answer the subsequent question. If the answer cannot be found, write "I don't know."

        Letter:
        \"\"\"
        {document_object.text}
        \"\"\"

        Question: Are there any sensitive information in this letter? Like bank account number or bank balance. If yes, write them down in bullet points. If no, say: There are no sensitive information"""

        response2 = openai.chat.completions.create(
            messages=[
                {'role': 'system', 'content': 'You answer regarding the sensitive information in the email.'},
                {'role': 'user', 'content': query2},
            ],
            model=GPT_MODEL,
            temperature=0,
        )

        print(response.choices[0].message.content)
        bounds = []
        for page in document_object.pages:
                for block in page.blocks:
                    bounds.append(block.layout.bounding_poly)
        img = draw_boxes(image, bounds, "yellow")

        if checkbox_ocr:
             st.image(img)
             st.subheader('Detected Letter', divider='blue')
             st.success( str(document_object.text) )

        if checkbox_recipient:
             st.subheader('Recipient of the letter', divider='blue')
             st.success("The recipient of the email is: " + str(response.choices[0].message.content) )
             #st.markdown(":blue[str(response.choices[0].message.content)]")
             st.button("Send to "+ str(response.choices[0].message.content) )

        if checkbox_summary: 
             st.subheader('Summary of the letter', divider='blue')
             st.success( str(response1.choices[0].message.content) )

        if checkbox_sensitive:
             st.subheader('Sensitive information', divider='blue')
             st.success(str(response2.choices[0].message.content) )