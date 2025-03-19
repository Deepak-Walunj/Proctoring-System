import pymongo as py
from PIL import Image
import io
import matplotlib.pyplot as plt
from bson import ObjectId

client=py.MongoClient("mongodb://localhost:27017/")
db=client["CandidateFace"]
coll=db["Faces"]

def retriveImage(id):
    image=coll.find_one({"_id":ObjectId(f"{id}")})
    print(image)
    pil_img = Image.open(io.BytesIO(image['data']))
    print(type(pil_img))
    plt.imshow(pil_img)
    plt.show()
    
if __name__=="__main__":
    id="67a5e679ea7444ad54bb5d17"
    retriveImage(id)