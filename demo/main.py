r"""
pip install uvicorn[standard]
pip install fastapi


C:\VirtualEnvs\wayfarer\Scripts\activate.ps1
cd D:\GitHub\wayfarer\demo
uvicorn main:app --reload --port 8020  --log-level 'debug'

http://127.0.0.1:8020/docs
http://127.0.0.1:8020

"""

from fastapi import FastAPI

# https://fastapi.tiangolo.com/tutorial/cors/
from fastapi.middleware.cors import CORSMiddleware
import wayfarer
import logging

from demo import edges, isochrones, rivers, routes

app = FastAPI()

app.include_router(edges.router)
app.include_router(isochrones.router)
app.include_router(rivers.router)
app.include_router(routes.router)


origins = ["http://localhost:8020", "*"]  # local development

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # True, can only have True here with a specific set of origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# set the following to ensure there is output to the console
# uvicorn sets the level to warning otherwise
logging.basicConfig(level=logging.DEBUG)

# logging.basicConfig(
#    filename=config.get_appconfig().log_file,
#    level=logging.DEBUG,
#    format="%(asctime)s:%(levelname)s:%(module)s:%(funcName)s: %(message)s",
#    datefmt="%Y-%m-%d %H:%M:%S",
# )

# log = logging.getLogger("wayfarer")

log = logging.getLogger("web")
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# log.addHandler(ch)


@app.get("/")
async def root():
    return "Hello from the Wayfarer Web Example (wayfarer version {})!".format(
        wayfarer.__version__
    )
