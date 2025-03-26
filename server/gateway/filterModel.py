from pydantic import BaseModel, Field
from typing import List, Dict, TypeAlias
from ..category.categoryModel import Category, CategoryOutObject
from ..base.pyObjectId import PyObjectId
from ..base.baseModelNew import BaseModelNew


FilterOutObject: TypeAlias = Dict[str, str | CategoryOutObject]


class Filter(BaseModelNew):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    category: Category


class FilterCreate(BaseModel):
    name: str
    category: str

class FilterCreateMany(BaseModel):
    name: List[str]
    category: Category
