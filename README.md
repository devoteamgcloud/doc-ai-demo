<!-- ABOUT THE PROJECT -->
## About The Project

This demo illustrates the capabilities of Document AI and Gemini.

## Deploy the app locally
- Create a document AI processor , in this case , it is an OCR type processor.
- Create a .env file with the following environment variables:
   ```sh
   PROJECT_ID='YOUR_PROJECT_ID'
   LOCATION='eu'
   PROCESSOR_ID ='YOUR_DOCUMENT_AI_PROCESSOR_ID'
   ```
- Create a Dockerfile file 
- Build the image locally, cd into your project folder and run. 
   ```sh
   docker buildx build .
   ```

- Run the docker image using the application default credentials used for authentication.
   ```sh
   docker run -v "Path to you loclal application default credentials i.e application_default_credentials.json":/gcp/creds.json:ro  --env GOOGLE_APPLICATION_CREDENTIALS=/gcp/creds.json -p 8080:8080  "YOUR_DOCKER_IMAGE"
   ```
- Access the app via the localhost.

## Deploy the app on cloud run 
- Create a document AI processor , in this case , it is an OCR type processor.
- Create a .env file with the following environment variables:
   ```sh
   PROJECT_ID='YOUR_PROJECT_ID'
   LOCATION='eu'
   PROCESSOR_ID ='YOUR_DOCUMENT_AI_PROCESSOR_ID'
   ```
- Create a Dockerfile file 
- Build the image and push it to conatiner registry
   ```sh
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/DEMO_NAME_OF_YOUR_CHOICE --timeout=1h
   ```
- Create a service in cloud run based on the built image. 
- Access the app via the link provided by the cloud run service.

