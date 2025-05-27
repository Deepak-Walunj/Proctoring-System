from django.http import JsonResponse
from PIL import Image
from io import BytesIO
import base64
import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))

from proctoring.detection_classes.centralisedDatabaseOps import DatabaseOps

def fetch_image_by_name(request, name):
    dbOps = DatabaseOps()
    image, status, message = dbOps.take_photo_from_database(name)

    if status and image:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return JsonResponse({
            "success": True,
            "message": message,
            "base64": img_base64,
            "name": name,
        })
    else:
        return JsonResponse({
            "success": False,
            "message": message,
            "base64": None,
        })


