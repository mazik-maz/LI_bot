FROM python:3.12.8
WORKDIR /bot
COPY . /bot
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]
