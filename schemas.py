from pydantic import BaseModel


# schema for adding products in database using 'localhost/docs' page
class CreateProduct(BaseModel):
    name: str
    price: float
    weight: float
    image_url: str
