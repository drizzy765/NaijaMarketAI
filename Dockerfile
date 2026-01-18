# 1. Use an official lightweight Python image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy necessary files
# We need the code, the trained models, and the historical data (for charts)
COPY main.py .
COPY all_models.pkl .
COPY final_dataset_cleaned_v3.csv .

# 4. Install dependencies
# We list them directly here to keep it simple, or you can use requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn pandas scikit-learn numpy pydantic

# 5. Expose the port the API runs on
EXPOSE 8000

# 6. Command to start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]