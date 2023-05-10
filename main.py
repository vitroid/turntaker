import platform
import random
import string
from logging import DEBUG, INFO, basicConfig, getLogger

import tinydb as ti
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

if platform.uname().node == "vitroid-brass.local":
    # ローカルデバッグ。
    BASEURL="http://127.0.0.1:8000"
    BASEPATH="."
else:
    # Deployする場合。(環境変数でとれないかな)
    BASEURL="https://turntaker.fly.dev"
    BASEPATH="/data"

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


occasions = ti.TinyDB(f"{BASEPATH}/occasions.json")
tokens = ti.TinyDB(f"{BASEPATH}/tokens.json")


@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def new_occasion():
    q = ti.Query()
    while True:
        admin = get_random_string(8)
        if len(occasions.search(q.admin == admin)) == 0:
            record = {"admin": admin,
                      "occasion_id": get_random_string(8),
                      "count": 1,
                      "waiting": 1,
                      "title": "Title"}
            occasions.insert(record)
            return record


@app.get("/new")
def new():
    """Create a new occasion.

    Returns:
        occasion_id: string
    """
    record = new_occasion()
    return record


@app.get("/q/{token}")
def query(token:str):
    q = ti.Query()
    trecords = tokens.search(q.token == token)
    if len(trecords) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    if len(trecords) != 1:
        raise HTTPException(status_code=404, detail="Invalid item")
    occasion_id = trecords[0]["occasion_id"]
    records = occasions.search(q.occasion_id == occasion_id)
    record = records[0]
    record["admin"] = ""
    return {"token": token,
            "title": record["title"],
            "count": record["count"],
            "waiting": trecords[0]["waiting"]}


@app.get("/r/{occasion_id}")
def reserve(occasion_id:str):
    q = ti.Query()
    records = occasions.search(q.occasion_id == occasion_id)
    if len(records) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    if len(records) != 1:
        raise HTTPException(status_code=404, detail="Invalid item")
    record = records[0]
    # 現在見えている番号を発行する。
    while True:
        token = get_random_string(8)
        if len(tokens.search(q.token == token)) == 0:
            trecord = {"token": token,
                      "occasion_id": occasion_id,
                      "waiting": record["waiting"]}
            tokens.insert(trecord)

            # 待ち番号を1増やす。
            waiting = record["waiting"] + 1
            occasions.update({"waiting": waiting},
                             q.occasion_id == occasion_id)

            return trecord


@app.get("/set/{admin}/{count}")
def set_count(admin:str, count:int):
    q = ti.Query()
    records = occasions.search(q.admin == admin)
    if len(records) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    if len(records) != 1:
        raise HTTPException(status_code=404, detail="Invalid item")
    logger.debug(records[0])
    # record = records[0]
    # newcount = record["count"]+1
    if count > 0:
        occasions.update({"count": count}, q.admin == admin)
        records = occasions.search(q.admin == admin)
    return records[0]


@app.get("/t/{admin}/{title}")
def set_title(admin:str, title:str):
    q = ti.Query()
    records = occasions.search(q.admin == admin)
    if len(records) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    if len(records) != 1:
        raise HTTPException(status_code=404, detail="Invalid item")
    logger.debug(records[0])
    # record = records[0]
    # newcount = record["count"]+1
    occasions.update({"title": title}, q.admin == admin)
    records = occasions.search(q.admin == admin)
    return records[0]


# 一応APIとして作ったけど、UIを別に準備するのが面倒なので、その場表示もする。
@app.get("/customer/{token}", response_class=HTMLResponse)
async def query_UI(request:Request, token:str):
    trecord = query(token)
    return templates.TemplateResponse("Q.html", {"request": request,
                                                 "baseurl": BASEURL}
                                                 | trecord)


@app.get("/", response_class=RedirectResponse)
async def new_UI(request:Request):
    record = new()
    admin = record["admin"]
    return RedirectResponse(f"{BASEURL}/admin/{admin}")


@app.get("/Set/{admin}/{count}", response_class=RedirectResponse)
async def set_UI(admin:str, count:int, request:Request):
    record = set_count(admin, count)
    return RedirectResponse(f"{BASEURL}/admin/{admin}")


@app.get("/admin/{admin}", response_class=HTMLResponse)
async def admin_UI(admin:str, request:Request):
    record = set_count(admin, 0)
    return templates.TemplateResponse("A.html", {"request": request,
                                                 "inc": record["count"]+1,
                                                 "dec": record["count"]-1,
                                                 "baseurl": BASEURL}
                                                 | record)


@app.get("/R/{occasion_id}", response_class=RedirectResponse)
async def reserve_UI(request:Request, occasion_id:str):
    trecord = reserve(occasion_id)
    token = trecord["token"]
    return RedirectResponse(f"{BASEURL}/customer/{token}")
