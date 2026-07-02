from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analytics import router as analytics_router
from app.routes.classes import router as classes_router
from app.routes.concepts import router as concepts_router
from app.routes.dictionary import router as dictionary_router
from app.routes.health import router as health_router
from app.routes.predictions import router as predictions_router
from app.routes.relations import router as relations_router
from app.routes.themes import router as themes_router
from app.routes.terms import router as terms_router
from app.routes.patents import router as patents_router
from app.routes.chat import router as chat_router
from app.routes.dashboard import router as dashboard_router



from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="Patent AI Lab API", version="0.1.0")
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(terms_router)
app.include_router(patents_router)
app.include_router(classes_router)

app.include_router(themes_router)
app.include_router(relations_router)
app.include_router(concepts_router)
app.include_router(analytics_router)
app.include_router(predictions_router)
app.include_router(dictionary_router)
app.include_router(chat_router)
app.include_router(dashboard_router)


