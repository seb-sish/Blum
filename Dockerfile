FROM python:3.12.2
WORKDIR /root/app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "/root/app/main.py", "1"]