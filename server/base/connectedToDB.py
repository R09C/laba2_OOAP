from abc import ABC, abstractmethod
from pymongo import MongoClient
from pymongo.collection import Collection


class Base(ABC):
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/test")
        self.db = self.client["test"]

    @abstractmethod
    def set_collection(self) -> Collection:
        pass


# docker run -d --name mongodb-container -p 27017:27017 mongo:latest
# 