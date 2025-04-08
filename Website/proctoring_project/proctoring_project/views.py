from django.http import JsonResponse
from django.middleware.csrf import get_token

def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})
def upload_video(request):
    if request.method == "POST":
        video_file = request.FILES.get("video")
        if video_file:
            # You can process the video here (save it to disk, process it, etc.)
            return JsonResponse({"message": "Video uploaded successfully!"})
        return JsonResponse({"error": "No video file provided"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)


