import os
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# आपकी ब्लॉगर वेबसाइट को इस सर्वर से कनेक्ट करने की अनुमति देने के लिए CORS सेटिंग
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # सुरक्षा के लिए बाद में यहाँ अपनी ब्लॉगर वेबसाइट का लिंक डालें
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# आपका Hugging Face टोकन यहाँ सेट कर दिया गया है
HF_TOKEN = "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"

# Hugging Face का वीडियो-टू-एनिमे (AnimateDiff) मॉडल API URL
HF_API_URL = "https://huggingface.co"

@app.post("/convert-video/")
async def convert_video(file: UploadFile = File(...)):
    # 1. जांचें कि अपलोड की गई फाइल वीडियो ही है
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="कृपया केवल वीडियो फाइल अपलोड करें।")
    
    try:
        # 2. वीडियो फाइल को बाइट्स (Bytes) में पढ़ना
        video_bytes = await file.read()
        
        # 3. Hugging Face API को रिक्वेस्ट भेजने के लिए हेडर्स तैयार करना
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }
        
        # 4. Hugging Face AI मॉडल को वीडियो भेजना
        print("वीडियो Hugging Face सर्वर पर प्रोसेस हो रहा है...")
        response = requests.post(HF_API_URL, headers=headers, data=video_bytes)
        
        # 5. अगर AI मॉडल अभी लोड हो रहा हो
        if response.status_code == 503:
            return {
                "status": "loading",
                "message": "AI मॉडल एक्टिवेट हो रहा है, कृपया 20-30 सेकंड बाद दोबारा कोशिश करें।",
                "estimated_time": response.json().get("estimated_time", 20)
            }
            
        # 6. अगर कोई दूसरी गड़बड़ हो
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"AI सर्वर त्रुटि: {response.text}")
            
        # 7. सफलतापूर्वक कनवर्टेड वीडियो मिलने पर
        return {
            "status": "success",
            "message": "वीडियो सफलतापूर्वक एनिमे में बदल दिया गया है!",
            "contentType": response.headers.get("Content-Type", "video/mp4")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"सर्वर एरर: {str(e)}")
  
