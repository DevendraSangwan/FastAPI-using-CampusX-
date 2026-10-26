from fastapi import FastAPI

app=FastAPI()
@app.get("/")
def see_data():
    return {"message":"hello World !"}


@app.get("/about")
def about():
    return {"message":"it's about "}