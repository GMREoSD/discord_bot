FROM python:3.11.5
WORKDIR /bot

RUN apt-get -y update && apt-get -y install locales && apt-get -y upgrade && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

# pip install
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot

# ポート番号8080解放
EXPOSE 8080

CMD python app/main.py
