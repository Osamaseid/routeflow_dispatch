from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from router import router

app = FastAPI()

app.include_router(router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )


@app.get("/")
def root():
    return {"message": "RouteFlow Webhook Service Running"}