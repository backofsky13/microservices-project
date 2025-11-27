from fastapi import FastAPI
from promocode_router import router as promocode_router

app = FastAPI(
    title="Promocode Service",
    description="Сервис управления промокодами для системы доставки продуктов",
    version="1.0.0"
)

app.include_router(promocode_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "promocode"}

@app.get("/")
def root():
    return {"message": "Promocode Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)