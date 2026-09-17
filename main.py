import os
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Social-craft AI Video Converter",
    description="यह बैकएंड सर्वर वीडियो को एनिमे में बदलने का काम करता है।",
    version="1.0"
)

# आपकी ब्लॉगर वेबसाइट या फ्रंटएंड को इस सर्वर से कनेक्ट करने की अनुमति देने के लिए CORS सेटिंग
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # सुरक्षा के लिए बाद में यहाँ अपनी ब्लॉगर वेबसाइट का लिंक डालें
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# सुरक्षा चेतावनी: टोकन को कोड के अंदर सीधे (Hardcode) न लिखें!
# Render के 'Environment Variables' में जाकर HF_TOKEN नाम से अपनी टोकन वैल्यू सेट करें।
HF_TOKEN = os.getenv("HF_TOKEN", "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")

# Hugging Face का वीडियो-टू-एनिमे मॉडल API URL
# नोट: Hugging Face से वीडियो प्रोसेस करने के लिए आपको सही मॉडल एंडपॉइंट URL की ज़रूरत होगी।
HF_API_URL = "https://huggingface.co" 

# 1. होम रूट (Home Route - GET request)
# अब मुख्य लिंक (https://onrender.com) खोलने पर एरर नहीं आएगा, बल्कि यह मैसेज दिखेगा।
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Social-craft AI Video Converter Backend सफलतापूर्वक चल रहा है!",
        "documentation": "डॉक्यूमेंटेशन देखने के लिए /docs या /redoc पर जाएं"
    }

# 2. वीडियो कन्वर्ट करने का रूट (POST request)
@app.post("/convert-video/")
async def convert_video(file: UploadFile = File(...)):
    # जांचें कि अपलोड की गई फ़ाइल वीडियो ही है
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="कृपया केवल वीडियो फ़ाइल अपलोड करें।")
    
    try:
        # वीडियो फ़ाइल को बाइट्स (Bytes) में पढ़ना
        video_bytes = await file.read()
        
        # Hugging Face API के लिए हेडर्स
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }
        
        # Hugging Face AI मॉडल को वीडियो भेजना
        print("वीडियो Hugging Face सर्वर पर प्रोसेस हो रहा है...")
        response = requests.post(HF_API_URL, headers=headers, data=video_bytes)
        
        # अगर AI मॉडल अभी लोड हो रहा हो (Loading State)
        if response.status_code == 503:
            return {
                "status": "loading",
                "message": "AI मॉडल एक्टिवेट हो रहा है, कृपया 20-30 सेकंड बाद दोबारा कोशिश करें।",
                "estimated_time": response.json().get("estimated_time", 20)
            }
            
        # अगर कोई दूसरी गड़बड़ हो
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"AI सर्वर त्रुटि: {response.text}")
            
        # सफलतापूर्वक कनवर्टेड वीडियो मिलने पर
        return {
            "status": "success",
            "message": "वीडियो सफलतापूर्वक एनिमे में बदल दिया गया है!",
            "contentType": response.headers.get("Content-Type", "video/mp4")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"सर्वर एरर: {str(e)}")
