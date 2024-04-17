import streamlit as st 
from PIL import Image, ImageDraw
import os 
from dotenv import load_dotenv
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models


load_dotenv()
PROJECT_ID =  os.getenv("PROJECT_ID")
LOCATION =  os.getenv("LOCATION")
PROCESSOR_ID = os.getenv("PROCESSOR_ID")

vertexai.init(project=PROJECT_ID, location="us-central1")
model = GenerativeModel("gemini-1.0-pro-vision-001")


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


st.set_page_config(
    page_title="Dokumentanalyse",
    page_icon = ":mailbox_with_mail:",
    initial_sidebar_state = 'auto'
)


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
        st.image('docai.png')
        st.title("Dokumentanalyse App")
        st.subheader("Diverse Möglichkeiten zur Analyse und Verarbeitung von Dokumenten, wie zum Beispiel Klassifikation, Informationsextraktion, Übersetzung, Zusammenfassung, etc ")

st.write("""
         # Dokumentanalyse
         """
         )


file = st.file_uploader("", type=["jpg", "png"])
checkbox_summary = st.checkbox("Zusammenfassung", value=True)
checkbox_recipient = st.checkbox("Empfänger erkennen", value=True)
checkbox_ocr = st.checkbox("Texterkennung", value=True)
checkbox_sensitive = st.checkbox("Sensible Information extrahieren", value=True)

# Every form must have a submit button.
columns = st.columns((2, 1, 2))
submitted = columns[1].button('Start')

if file is None:
    st.text("Bitte laden Sie ein Bild hoch")
else:
    path = os.path.join(os.getcwd(), file.name)
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
        print("Dokumentverarbeitung abgeschlossen.")

        bounds = []
        for page in document_object.pages:
                for block in page.blocks:
                    bounds.append(block.layout.bounding_poly)
        img = draw_boxes(image, bounds, "yellow")

        image1 = Part.from_data(data=image_content, mime_type="image/jpeg")

        responses = model.generate_content(
    [image1, """Who is the recipient of the email? Please provide only the answer with no introductions. Provide the answer in German."""],
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32
    },
    safety_settings={
          generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    },
    stream=True,
  ) 
      
        resp = ""
        for response in responses:
             resp+= str(response.text)

        responses1 = model.generate_content(
    [image1, """Summarize the text in the image and answer in German. If the answer cannot be found, write 'Ich weiß es nicht'."""],
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32
    },
    safety_settings={
          generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    },
    stream=True,
  ) 
        resp1 = ""
        for response in responses1:
             resp1+= str(response.text)

        responses2 = model.generate_content(
    [image1, """Are there any sensitive information in this letter? Like bank account number or bank balance. If yes, write them down in bullet points in german. If no, say: Keine sensiblen Informationen gefunden."""],
    generation_config={
        "max_output_tokens": 2048,
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32
    },
    safety_settings={
          generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
          generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    },
    stream=True,
  ) 
        resp2 = ""
        for response in responses2:
             resp2+= str(response.text)

        if checkbox_ocr:
             st.image(img)
             st.subheader('Textextraktion', divider='blue')
             st.success( str(document_object.text) )

        if checkbox_recipient:
             st.subheader('Empfänger', divider='blue')
             st.success("Der/Die Empfänger*in: " + str(resp[0]) )
             st.button("Weiterleiten an "+ str(resp) )

        if checkbox_summary: 
             st.subheader('Zusammenfassung', divider='blue')
             st.success( str(resp1) )

        if checkbox_sensitive:
             st.subheader('Sensible Information', divider='blue')
             st.success(str(resp2))