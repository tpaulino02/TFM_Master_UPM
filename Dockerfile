ROM python:3

RUN apt-get update && apt-get install -y gettext && apt-get install -y cron 

ADD requirements.txt .

RUN pip install -r /Users/thiagopaulino/Documents/Mestrado_UPM/TFM/SentimentalAnalysis/NLTK/new_ppt/NLTK/participation-pipeline/requirements.txt --default-timeout=10000 --use-deprecated=legacy-resolver

WORKDIR /usr/src/app

ADD ./app /usr/src/app

# Cron service

RUN echo "00 3 * * * root cd /usr/src/app && python capture_twitter.py" >> /etc/crontab
RUN echo "00 3 * * * root cd /usr/src/app && python capture_subreddits.py" >> /etc/crontab


ENV PYTHONPATH=./

CMD sh cron.sh




