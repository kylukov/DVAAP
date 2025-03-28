from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()


# Основной эндпоинт
@app.get("/")
async def root():
    return {"message": "Hello World"}


# Эндпоинт для получения информации о товаре
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# Эндпоинт, который делает запрос к другому эндпоинту
@app.get("/call-internal-endpoint")
async def call_internal_endpoint():
    async with httpx.AsyncClient() as client:
        # Делаем запрос к внутреннему эндпоинту /items/42
        response = await client.get("http://127.0.0.1:8000/items/42?q=test")

        # Проверяем статус ответа
        if response.status_code == 200:
            return {
                "message": "Successfully called internal endpoint",
                "response_data": response.json()
            }
        else:
            return {
                "error": "Failed to call internal endpoint",
                "status_code": response.status_code
            }


# Эндпоинт для примера POST запроса
@app.post("/create-item/")
async def create_item(item: dict):
    return {
        "message": "Item created",
        "item": item
    }


# Эндпоинт, который делает POST запрос к /create-item/
@app.get("/call-create-item")
async def call_create_item():
    test_item = {
        "name": "Sample Item",
        "description": "This is a test item",
        "price": 9.99
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/create-item/",
            json=test_item
        )

        return {
            "message": "Called create-item endpoint",
            "response": response.json()
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)