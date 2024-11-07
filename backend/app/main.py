from fastapi import FastAPI
from .config.firebase import firebase
from .development import development
from .properties_management import properties


app = FastAPI()
app.debug = True


# setting up firebase
firebase.get_instance()

app.include_router(properties.router)
app.include_router(development.router)





        
