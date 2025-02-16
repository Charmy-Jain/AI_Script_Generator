import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import pytesseract
from PIL import Image
import pdfplumber

# Define maximum token limits based on video format
PLATFORM_MAX_TOKENS = {
    "instagram": 200,   # 150-200 words for 90 seconds
    "linkedin": 600,    # 300-500 words for engagement
    "tiktok": 350,      # 250-350 words for 3 min
    "youtube": 1000     # Flexible, longer content
}

def home(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_script(request):
    if request.method == "POST":
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        vibe = data.get("vibe", "casual")
        video_format = data.get("video_format", "youtube").lower()
        extracted_text = data.get("extracted_text", "")

        api_url = "https://intellivibe-ai.onrender.com/intellivibe/chat/ai_access?api_key=3067acd48938da0ba064b6c631cd2ad183b55d95fdff6a6c6eba4642098b87ad"
        api_key = "3067acd48938da0ba064b6c631cd2ad183b55d95fdff6a6c6eba4642098b87ad"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }


        payload = {
            "api_key": api_key,
            "chat": f"{prompt}\n{extracted_text}".strip(),  # Pass 'chat' instead of 'prompt'
            "vibe": vibe,
            "video_format": video_format
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response_data = response.json()

            # Debugging: Print API response to console
            print("API Response is:", response_data)

            # Extract script from response
            script = response_data
            if not script:
                return JsonResponse({"error": "API did not return a script.", "response": response_data}, status=500)

            return JsonResponse({"script": script})
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Request failed", "details": str(e)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid API response format"}, status=500)

    return JsonResponse({"error": "Invalid request."}, status=400)

@csrf_exempt
def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_path = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
        extracted_text = ""

        try:
            if uploaded_file.name.endswith(".txt"):
                with open(file_path, "r") as f:
                    extracted_text = f.read()
            elif uploaded_file.name.endswith(".pdf"):
                with pdfplumber.open(default_storage.path(file_path)) as pdf:
                    extracted_text = " ".join(
                        page.extract_text() for page in pdf.pages if page.extract_text()
                    )
            elif uploaded_file.content_type.startswith("image"):
                image = Image.open(file_path)
                extracted_text = pytesseract.image_to_string(image)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({"extracted_text": extracted_text})
    
    return JsonResponse({"error": "Invalid request."}, status=400)

@csrf_exempt
def fetch_metadata(request):
    if request.method == "POST":
        data = json.loads(request.body)
        url = data.get("url", "")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Truncate for simplicity
                return JsonResponse({"metadata": response.text[:1000]})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request."}, status=400)
