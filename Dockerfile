FROM python:3

COPY flask_requirements.txt ./
RUN pip install --no-cache-dir -r flask_requirements.txt

COPY flask_main.py ./

CMD ["gunicorn", "flask_main:app", "-b", "0.0.0.0:80", "-w", "4"]
