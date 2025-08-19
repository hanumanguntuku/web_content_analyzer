from fastapi import FastAPI
from .api import routes, middleware

app = FastAPI(title="web_content_analyzer")
app.add_middleware(middleware.SimpleLoggingMiddleware)
app.include_router(routes.router)

@app.get('/health')
async def health():
    return {'status': 'ok'}
