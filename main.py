import random
import string
from logging import DEBUG, INFO, basicConfig, getLogger

import tinydb as ti
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Deployする場合。(環境変数でとれないかな)
BASEURL="https://turntaker.fly.dev"
# ローカルデバッグ。
# BASEURL="http://127.0.0.1:8000"

basicConfig(level=DEBUG)
logger = getLogger()

templates = Jinja2Templates(directory="templates")

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db = ti.TinyDB("db.json")


@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def new_session():
    query = ti.Query()
    while True:
        admin = get_random_string(8)
        if len(db.search(query.admin == admin)) == 0:
            record = {"admin": admin,
                      "token": get_random_string(8),
                      "count": 1,
                      "remark": "現在の順番"}
            db.insert(record)
            return record


@app.get("/new")
def new():
    """Create a new session.

    Returns:
        token: string
    """
    record = new_session();
    return record


@app.get("/q/{token}")
def query(token:str):
    q = ti.Query()
    records = db.search(q.token == token)
    if len(records) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    if len(records) != 1:
        raise HTTPException(status_code=404, detail="Invalid item")
    logger.debug(records[0])
    record = records[0]
    record["admin"] = ""
    return record


@app.get("/set/{admin}/{count}")
def set_count(admin:str, count:int):
    q = ti.Query()
    records = db.search(q.admin == admin)
    if len(records) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    if len(records) != 1:
        raise HTTPException(status_code=404, detail="Invalid item")
    logger.debug(records[0])
    # record = records[0]
    # newcount = record["count"]+1
    db.update({"count": count}, q.admin == admin)
    records = db.search(q.admin == admin)
    return records[0]


# 一応APIとして作ったけど、UIを別に準備するのが面倒なので、その場表示もする。
@app.get("/Q/{token}", response_class=HTMLResponse)
async def query_UI(request:Request, token:str):
    record = query(token)
    return templates.TemplateResponse("Q.html", {"request": request,
                                                 "baseurl": BASEURL}
                                                 | record)


@app.get("/New", response_class=HTMLResponse)
async def new_UI(request:Request):
    logger.debug("New")
    record = new()
    logger.debug(record)
    return templates.TemplateResponse("A.html", {"request": request,
                                                 "inc": record["count"]+1,
                                                 "dec": record["count"]-1,
                                                 "baseurl": BASEURL}
                                                 | record)


@app.get("/Set/{admin}/{count}", response_class=HTMLResponse)
async def set_UI(admin:str, count:int, request:Request):
    record = set_count(admin, count)
    return templates.TemplateResponse("A.html", {"request": request,
                                                 "inc": record["count"]+1,
                                                 "dec": record["count"]-1,
                                                 "baseurl": BASEURL}
                                                 | record)
