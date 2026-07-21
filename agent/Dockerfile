FROM python:3.14-slim

WORKDIR /agent

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "agent.server:app", "--host", "0.0.0.0", "--port", "8000"]
