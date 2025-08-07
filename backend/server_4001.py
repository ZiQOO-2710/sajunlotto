from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import crud, models, schemas, crawler
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SajuLotto API", description="Korean fortune-telling based lottery prediction API")

@app.get("/")
def read_root():
    return {"message": "SajuLotto API is running on port 4001!", "status": "success", "version": "1.0.0"}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def crawl_lotto_task(start_draw: int, end_draw: int):
    """
    Background task for crawling lotto data.
    A new DB session is created for this task.
    """
    db = SessionLocal()
    try:
        print(f"Starting to crawl lotto draws from {start_draw} to {end_draw}...")
        count = 0
        for draw_no in range(start_draw, end_draw + 1):
            result = crawler.crawl_and_save_lotto_draw(db, draw_no)
            if result:
                count += 1
        print(f"Crawling finished. Saved {count} new draws from {start_draw} to {end_draw}.")
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/users/{user_id}/saju/", response_model=schemas.SajuProfile)
def create_saju_profile_for_user(
    user_id: int, saju_profile: schemas.SajuProfileCreate, db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_saju_profile(db=db, user_id=user_id, saju_profile=saju_profile)

@app.post("/admin/crawl_lotto_draws/")
def admin_crawl_lotto_draws(
    start_draw: int,
    end_draw: int,
    background_tasks: BackgroundTasks
):
    """
    Triggers a background task to crawl and save lotto draws for a given range.
    """
    background_tasks.add_task(crawl_lotto_task, start_draw, end_draw)
    return {"message": f"Crawling for draws {start_draw} to {end_draw} has been initiated in the background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=4001)