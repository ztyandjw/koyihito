class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str = None

class Item(BaseModel):
    id: int
    title: str
    description: str = None
    owner_id: int

class UserInDB(User):
    hashed_password: str