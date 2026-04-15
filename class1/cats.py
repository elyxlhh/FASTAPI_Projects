# =============================================================================
# PATH PARAMETERS vs QUERY PARAMETERS
# =============================================================================
#
# PATH PARAMETER
#   - Embedded directly in the URL path using curly braces: /cats/{cat_name}
#   - Always required — the route won't match without it
#   - Use when the value IDENTIFIES a specific resource
#   - Example: GET /cats/name-one  →  retrieves one specific cat
#
# QUERY PARAMETER
#   - Appended to the URL after "?": /cats/gender?gender=male
#   - Can be optional (assign a default value, e.g. gender: str = None)
#   - Use when the value FILTERS or SEARCHES a collection
#   - Example: GET /cats/gender?gender=male  →  filters cats by gender
#   - Multiple query params: /cats/search?hospital=H1&cat_color=black&gender=male
#
# QUICK RULE OF THUMB
#   - Fetching one specific resource  →  path parameter  (/cats/{cat_name})
#   - Filtering / searching a list    →  query parameter (/cats/gender?gender=male)
#
# =============================================================================
# ROUTE ORDERING RULES (important in FastAPI!)
# =============================================================================
#
# FastAPI matches routes TOP TO BOTTOM and stops at the first match.
# Incorrect ordering causes routes to be silently shadowed (never reached).
#
# CORRECT ORDER:
#   1. Static paths first          e.g. /cats/gender, /cats/search
#   2. Path+query mixed paths      e.g. /cats/hospital/{hospital_name}
#   3. Dynamic path params last    e.g. /cats/{cat_name}
#
# WHY: /cats/{cat_name} will match ANY single-segment path under /cats/,
# including /cats/gender and /cats/search, so it must come last.
#
# TRAILING SLASH WORKAROUND (avoid this):
#   Defining /cats/gender/ (with slash) makes it distinct from /cats/{cat_name},
#   so it won't be shadowed even if declared after the dynamic route.
#   However, this is a hack — prefer correct ordering instead.
#
# =============================================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Cat(BaseModel):
    name: str
    hospital: str
    color: str
    gender: str

class CatUpdate(BaseModel):
    hospital: Optional[str] = None
    color: Optional[str] = None
    gender: Optional[str] = None

CATS = [
    {'name': 'Name One', 'hospital': 'Hospital One', 'color': 'black', 'gender': 'male'},
    {'name': 'Name Two', 'hospital': 'Hospital Two', 'color': 'white', 'gender': 'female'},
    {'name': 'Name Three', 'hospital': 'Hospital Three', 'color': 'orange', 'gender': 'male'},
    {'name': 'Name Four', 'hospital': 'Hospital Four', 'color': 'gray', 'gender': 'female'},
    {'name': 'Name Five', 'hospital': 'Hospital Five', 'color': 'white', 'gender': 'female'},
    {'name': 'Name Six', 'hospital': 'Hospital Two', 'color': 'black', 'gender': 'male'}
]

@app.get("/")
async def root():
    return {"message": "This is the root"}

# static path first, then query parameter, then path parameter
@app.get("/cats")
async def read_all_cats():
    return CATS

@app.get("/cats/gender")
async def read_cat_by_gender(gender: str):
    res = []
    for cat in CATS:
        if cat.get('gender').casefold() == gender.casefold():
            res.append(cat)
    return res

@app.get("/cats/hospital")
async def read_cat_by_hospital(hospital: str):
    return [cat for cat in CATS if cat.get('hospital').casefold() == hospital.casefold()]

@app.get("/cats/search")
async def thorough_cat_search(hospital: str, cat_color: str, gender: str):
    res = []
    for cat in CATS:
        if cat.get('hospital').casefold() == hospital.casefold() and \
                cat.get('color').casefold() == cat_color.casefold() and \
                cat.get('gender').casefold() == gender.casefold():
            res.append(cat)
    return res

@app.get("/cats/hospital/{hospital_name}")
async def search_cats_by_hospital(hospital_name: str, gender: str = None):
    res = [cat for cat in CATS if cat.get('hospital').casefold() == hospital_name.casefold()]
    if gender:
        res = [cat for cat in res if cat.get('gender').casefold() == gender.casefold()]
    return res

@app.get("/cats/{cat_name}")
async def read_cat_by_name(cat_name: str):
    for cat in CATS:
        if cat.get('name').casefold() == cat_name.casefold():
            return cat
    raise HTTPException(status_code=404, detail="Cat not found")

@app.post("/cats/add")
async def add_cat(cat: Cat):
    if cat.name.casefold() in [c.get('name').casefold() for c in CATS]:
        raise HTTPException(status_code=400, detail="Cat with this name already exists")
    CATS.append(cat.model_dump())
    return {"message": "Cat added successfully"}

@app.put("/cats/update_name/")
async def update_cat(cat_name: str, cat: CatUpdate):
    for c in CATS:
        if c.get('name').casefold() == cat_name.casefold():
            c.update({k: v for k, v in cat.model_dump().items() if v is not None})
            return {"message": "Cat updated successfully"}
    raise HTTPException(status_code=404, detail="Cat not found")

@app.delete("/cats/delete/{cat_name}")
async def delete_cat(cat_name: str):
    for c in CATS:
        if c.get('name').casefold() == cat_name.casefold():
            CATS.remove(c)
            return {"message": "Cat deleted successfully"}
    raise HTTPException(status_code=404, detail="Cat not found")
