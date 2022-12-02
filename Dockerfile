FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/

RUN rm requirements.txt

COPY ./ /app/
