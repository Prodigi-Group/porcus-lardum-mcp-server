# function_app.py

import azure.functions as func 
from server import app

app = func.AsgiFunctionApp(
    app=app,
    http_auth_level=func.AuthLevel.ANONYMOUS
)
