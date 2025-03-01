#Use Python 3.10 as base image
FROM python:3.10

#Set Working directory inside the container
WORKDIR /app

#Copy project files into container
COPY . /app

#Install Dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

#Expose FastAPI port
EXPOSE 8000

#Run FastAPI app
CMD ["uvicorn", "fastapi_library_app:app", "--host", "--port", "8000"]