from fastapi import FastAPI, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Cat:
    id: int
    name: str
    color: str
    gender: str
    birthyear: int

    def __init__(self, id, name, color, gender, birthyear):
        self.id = id
        self.name = name
        self.color = color
        self.gender = gender
        self.birthyear = birthyear

class CatUpdate(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    name: str = Field(min_length=3)
    color: str = Field(min_length=1, max_length=20)
    gender: str = Field(min_length=1, max_length=10)
    birthyear: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Bob",
                "color": "black",
                "gender": "male",
                "birthyear": 2020
            }
        }
    }

CATS = [
    Cat(1, 'Name One', 'black', 'male', 2025),
    Cat(2, 'Name Two', 'white', 'female', 2024),
    Cat(3, 'Name Three', 'orange', 'male', 2025),
    Cat(4, 'Name Four', 'gray', 'female', 2024),
    Cat(5, 'Name Five', 'white', 'female', 2024),
    Cat(6, 'Name Six', 'black', 'male', 2025)
]

@app.get("/")
async def root():
    return {"message": "This is the root"}

# static path first, then query parameter, then path parameter
@app.get("/cats", status_code=status.HTTP_200_OK)
async def read_all_cats():
    return CATS

@app.get("/cats/gender", status_code=status.HTTP_200_OK)
async def read_cat_by_gender(gender: str):
    res = []
    for i in range(len(CATS)):
        if CATS[i].gender.casefold() == gender.casefold():
            res.append(CATS[i])
    if res == []:
        raise HTTPException(status_code=404, detail="No cats found with this gender")
    return res

@app.get("/cats/birthyear", status_code=status.HTTP_200_OK)
async def read_cat_by_birthyear(birthyear: int = Query(gt=2010, lt=2025)):
    res = []
    for i in range(len(CATS)):
        if CATS[i].birthyear == birthyear:
            res.append(CATS[i])
    if res == []:
        raise HTTPException(status_code=404, detail="No cats found with this birthyear")
    return res

@app.get("/cats/{cat_id}", status_code=status.HTTP_200_OK)
async def read_cat_by_id(cat_id: int = Path(gt=0)):
    for cat in CATS:
        if cat.id == cat_id:
            return cat
    raise HTTPException(status_code=404, detail="Cat not found")

def set_cat_id(cat: Cat):
    cat.id = 1 if len(CATS) == 0 else CATS[-1].id + 1
    return cat

@app.post("/cats", status_code=status.HTTP_201_CREATED)
async def add_cat(cat: CatUpdate):
    cat_to_add = Cat(**cat.model_dump())
    CATS.append(set_cat_id(cat_to_add))
    return {"message": "Cat added successfully"}

@app.put("/cats/update_name/", status_code=status.HTTP_204_NO_CONTENT)
async def update_cat(cat_name: str, cat: CatUpdate):
    for c in CATS:                                                                                                                                             
        if c.name.casefold() == cat_name.casefold():                                                                                                           
            c.name = cat.name
            c.color = cat.color                                                                                                                                
            c.gender = cat.gender
            c.birthyear = cat.birthyear                                                                                                                        
            return
    raise HTTPException(status_code=404, detail="Cat not found")

@app.delete("/cats/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cat(cat_id: int = Path(gt=0)):
    for i in range(len(CATS)):
        if CATS[i].id == cat_id:
            CATS.pop(i)
            return
    raise HTTPException(status_code=404, detail="Cat not found")
