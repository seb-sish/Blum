FROM python:3.12.5
WORKDIR /root/app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "/root/app/main.py", "1"]