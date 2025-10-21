from fastapi import FastAPI, status

app = FastAPI()

@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"message": "Great job, the server is running!"}