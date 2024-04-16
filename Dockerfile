FROM python:3.12.1
EXPOSE 8080
WORKDIR /app

ENV $(cat .env)

COPY . ./
RUN pip install -r requirements.txt
RUN python -c "import dotenv; dotenv.load_dotenv()"
ENTRYPOINT ["streamlit", "run", "demo_docai_gemini_ger.py", "--server.port=8080", "--server.address=0.0.0.0"]