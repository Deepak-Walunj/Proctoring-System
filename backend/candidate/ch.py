import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from client import database
from bson import ObjectId
import math

db=database()

collection = db['viva_reports']
# print(collection.delete_many({'name':'prathmesh@2004'}))
print(collection.delete_many({}))

