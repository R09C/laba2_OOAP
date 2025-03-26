from ..base.connectedToDB import Base


class MongoSave(Base):

    def __init__(self):
        super().__init__()
        self.collection = self.set_collection()

    def set_collection(self):
        return self.db["json_type"]

    def get_collection(self):
        return self.collection

    def save_json(self, body):
        result = self.collection.insert_one(body)
        return result.inserted_id

    def get_all(self):
        return list(self.collection.find())
