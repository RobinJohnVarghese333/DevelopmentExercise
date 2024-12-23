import datetime
from Accounts.mongo_client import db



Basic= db['Basic']
class PanModel:
    collection = Basic

    @staticmethod
    def create(panNumber, name):
        data = {
            "panNumber": panNumber,
            "name": name,
            "ipoStatus": None,
        }
        PanModel.collection.insert_one(data)
        return data

SelectedIposCollection= db['SelectedIposCollection']
class IpoModel:
    collection = SelectedIposCollection  

    @staticmethod
    def create(ipoChoice, panNumber):
        data = {
            "ipoChoice": ipoChoice,
            "panNumber": panNumber,
            "timestamp": datetime.utcnow().isoformat(),  
        }
        IpoModel.collection.insert_one(data)
        return data

    # @staticmethod
    # def get_all():
    #     return list(IpoModel.collection.find({}, {"_id": 0})) 

    # @staticmethod
    # def get_by_choice(ipoChoice):
    #     return list(IpoModel.collection.find({"ipoChoice": ipoChoice}, {"_id": 0}))

    # @staticmethod
    # def delete_by_choice(ipoChoice):
    #     return IpoModel.collection.delete_many({"ipoChoice": ipoChoice}).deleted_count
