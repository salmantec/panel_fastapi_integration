from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from core.config import settings
from apis.general_pages.route_homepage import general_pages_router
from apis.general_pages.panel_app import create_app

import panel as pn
from panel.io.fastapi import add_application

def include_router(app):
    app.include_router(general_pages_router)

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    return app
    
app = start_application()

@add_application("/panel", app=app, title="My panel app")
def create_panel_app():
    # slider = pn.widgets.IntSlider(name="Slider", start=0, end=10, value=3)
    # return slider.rx() * '⭐'
    return create_app()