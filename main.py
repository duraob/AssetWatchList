from fastapi import FastAPI, Request, Depends, BackgroundTasks, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import models
from models import Asset
from sqlalchemy.orm import Session
from db import Base, SessionLocal, engine
from pydantic import BaseModel
import yfinance


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

## Model for our Requests
class AssetRequest(BaseModel):
    symbol:str

## Connect to Database
def get_db():
    try:
        ## Create a session connection to the database
        db = SessionLocal()
        ## Return a generator - data that only needs to be read once
        yield db
    finally:
        db.close()


def fetch_asset_data(id: int):
    db = SessionLocal()
    ## Query the database for the passes parameter and select the first record.
    asset = db.query(Asset).filter(Asset.id == id).first()

    ## Make call to yahoo finance for lastest info
    ydata = yfinance.Ticker(asset.symbol)

    asset.quote = ydata.info['previousClose']
    asset.pe = ydata.info['forwardPE']
    if ydata.info['dividendYield'] is not None:
        asset.dividend = ydata.info['dividendYield'] * 100
    asset.ma50 = ydata.info['fiftyDayAverage']
    asset.ma200 = ydata.info['twoHundredDayAverage']

    ## Add object to database session
    db.add(asset)
    ## Commit changes to database
    db.commit()


## ROUTING
## Display stock screen dashboard homepage
## Search our DB for assets added and display them on the table.
@app.get('/')
def home(request: Request, ma50=None, ma200=None, db: Session = Depends(get_db)):
    assets = db.query(Asset)

    if ma50 is not None:
        assets = assets.filter(Asset.quote > Asset.ma50)
    if ma200 is not None:
        assets = assets.filter(Asset.quote > Asset.ma200)

    return templates.TemplateResponse('home.html', {
        'request': request,
        'assets': assets,
        'ma50' : ma50,
        'ma200' : ma200
        
    })

## Update the current assets in the database with latest quote
@app.get('/update')
async def update_assets(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    assets = db.query(Asset).all()

    for asset in assets:
        background_tasks.add_task(fetch_asset_data, asset.id)
    
    return assets

## Add Stock to DB based on data model, create a DB session, init a new obj to add based on 
@app.post('/asset')
async def create_asset(asset_request: AssetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ## This request will create a new asset object so instantiate it
    asset = Asset()
    ## From the body of the request model receive the data we want to map to our DB object
    asset.symbol = asset_request.symbol

    ## Add this object to the database session
    db.add(asset)
    ## Commit this object to the database and close the session
    db.commit()

    ## Add an async call to get the related data to our asset
    ## Pass a function and its parameter(s)
    background_tasks.add_task(fetch_asset_data, asset.id)

    return asset

## Remove stock from DB
@app.delete('/asset/{symbol}')
def delete_asset(symbol: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.symbol == symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail='Asset not found.')
    db.delete(asset)
    db.commit()
    return None
