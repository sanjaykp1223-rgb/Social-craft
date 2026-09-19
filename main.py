import os
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from gradio_client import Client  # नया क्लाइंट इम्पोर्ट किया

app = FastAPI(
    title="Social-craft AI Video Converter",
    description="यह बैकएंड सर्वर वीडियो को एनिमे में बदलने का काम करता है।",
    version="1.0"
)

# CORS सेटिंग
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# आपका Hugging Face टोकन
HF_TOKEN = os.getenv("HF_TOKEN", "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")

# 🔴 जरूरी बदलाव: यहाँ "nyijun/Video-to-Anime" की जगह अपने Hugging Face Space का सही नाम डालें
# उदाहरण के लिए अगर आप किसी एनीमेशन मॉडल का उपयोग कर रहे हैं तो उसका 'username/space-name' यहाँ आएगा।
HF_SPACE_NAME = "SpiderReddy/Video-to-Anime" 

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Social-craft AI Video Converter Backend सफलतापूर्वक चल रहा है!"
    }

@app.post("/convert-video/")
async def convert_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="कृपया केवल वीडियो फ़ाइल अपलोड करें।")
    
    # 1. वीडियो फाइल को टेम्परेरी लोकल सेव करना (Gradio Client के लिए जरूरी है)
    input_path = f"temp_{file.filename}"
    try:
        with open(input_path, "wb") as f:
            f.write(await file.read())
            
        print("वीडियो Hugging Face सर्वर पर प्रोसेस हो रहा है...")
        
        # 2. Gradio Client के जरिए सुरक्षित कनेक्शन बनाना
        client = Client(HF_SPACE_NAME, hf_token=HF_TOKEN)
        
        # 3. AI मॉडल को वीडियो भेजना (नोट: '/predict' आपके मॉडल के अनुसार बदल सकता है)
        result = client.predict(input_path, api_name="/predict")
        
        # प्रोसेस होने के बाद टेम्परेरी फाइल डिलीट करना
        if os.path.exists(input_path):
            os.remove(input_path)
            
        return {
            "status": "success",
            "message": "वीडियो सफलतापूर्वक एनिमे में बदल दिया गया है!",
            "converted_video_url": result  # यह आपको कनवर्टेड वीडियो का लिंक देगा
        }
        
    except Exception as e:
        # एरर आने पर भी टेम्परेरी फाइल डिलीट करना ताकि सर्वर की मेमोरी न भरे
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"AI सर्वर त्रुटि: {str(e)}")
