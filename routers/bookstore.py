#this is the main file, contain api/endpoints that we uses.
import sys
sys.path.append("..")

from typing import Optional, List
from pydantic import BaseModel
from fastapi import  Depends, HTTPException, UploadFile, APIRouter, File
from sqlalchemy.orm import Session
from datetime import datetime
import models, csv
from schemas import BookCreate, BookUpdate  
from database import engine, SessionLocal
from .auth import get_current_user, get_user_exception




router =APIRouter(
    prefix="",
    tags=["Book"],
    responses={401:{"user": "Not authorized"}}
    )

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()  



class BookStore(BaseModel):
    title: str
    author: str
    price: float
    published_date: datetime
    created_at: datetime
    updated_at: datetime
    user_id: int



@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.BookStore).all()



# @app.get("/bookstore/user")
# async def read_all_user(user: dict= Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     return db.query(models.BookStore)\
#         .filter(models.BookStore.user_id == user.get("id"))\
#         .all()    
#     return books 

# @app.get("/bookstore/user")
# async def read_all_user( user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     return db.query(models.BookStore)\
#         .filter(models.BookStore.user_id == user.get("id"))\
#         .all()
   
@router.get("/bookstore/user")
async def read_all_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    print("Current user ID:", user.get("id"))  # Add this line
    return db.query(models.BookStore)\
        .filter(models.BookStore.user_id == user.get("id"))\
        .all()   



@router.post("/")
async def create_book(book: BookCreate, 
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception
     
    book_model = models.BookStore(
        title=book.title,
        author=book.author,
        price=book.price,
        published_date=book.published_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=user.get("id")
       )
    
    db.add(book_model)
    db.commit()
    db.refresh(book_model)

    return book_model



@router.get("/{book_id}")
async def get_book(book_id: int,
                   user: dict = Depends(get_current_user), 
                   db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    book = db.query(models.BookStore)\
        .filter(models.BookStore.id == book_id)\
        .filter(models.BookStore.user_id == user.get("id"))\
        .first()
    if book is not None:
        return book
    raise HTTPException(status_code=404, detail="Book not found")



@router.put("/{book_id}")
async def update_book(book_id: int, 
                      book: BookUpdate, 
                      user: dict = Depends(get_current_user), 
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception
    
    book_model = db.query(models.BookStore)\
        .filter(models.BookStore.id == book_id)\
        .filter(models.BookStore.user_id == user.get("id"))\
        .first()
        
    if book_model is None:
        raise http_exception()
    if book.title is not None:
        book_model.title = book.title
    if book.author is not None:
        book_model.author = book.author
    if book.price is not None:
        book_model.price = book.price
    if book.published_date is not None:
        book_model.published_date = book.published_date
    if book.created_at is not None:
        book_model.created_at = book.created_at
    if book.updated_at is not None:
        book_model.updated_at = book.updated_at
    if book.user_id is not None:
        book_model.user_id = book.user_id               
        

    #book_model.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(book_model)
    
    return successful_response(200)



@router.get("/books")
async def search(
    limit: int = 10,
    author: Optional[str] = None,
    title: Optional[str] = None,
    db: Session = Depends(get_db)):
    
    query = db.query(models.BookStore)

    if author:
        query = query.filter(models.BookStore.author.ilike(f"%{author}%"))
    if title:
        query = query.filter(models.BookStore.title.ilike(f"%{title}%"))

    return query.limit(limit).all()



@router.delete("/{book_id}")
async def delete_book(book_id: int,
                      user: dict = Depends(get_current_user),
                      db:Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    
    book_model = db.query(models.BookStore)\
        .filter(models.BookStore.id == book_id)\
        .filter(models.BookStore.user_id == user.get("id"))\
        .first()
                    
    if book_model is None:
        raise http_exception()
    
    db.query(models.BookStore)\
        .filter(models.BookStore.id == book_id)\
        .delete()
        
    db.commit()        
    
    return successful_response(200)


# def process_csv(file: UploadFile, db: Session) -> int:
#     content = file.file.read().decode('utf-8').splitlines()
#     reader = csv.DictReader(content)
    
#     books_to_add = []
#     for row in reader:
#         book = BookStore(
#             title=row['title'],
#             author=row['author'],
#             price=row['price'],
#             published_date=row['published_date'],
#             created_at=row['created_at'],
#             updated_at=row['updated_at'],
#             isbn=row.get('isbn')
#         )
#         books_to_add.append(book)

#     db.bulk_save_objects(books_to_add)
#     db.commit()
#     return len(books_to_add)


# @router.post("/books/upload")
# def upload_books(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     if not file.filename.endswith('.csv'):
#         raise HTTPException(status_code=400, detail="File must be a CSV.")
    
#     count = process_csv(file, db)
#     return {"inserted": count}



def successful_response(status_code: int):
     return {
        'status': status_code,
        'transaction': 'Successful'
    } 
 
 
 
def http_exception():
    return HTTPException(status_code = 404, detail="Book not found")     