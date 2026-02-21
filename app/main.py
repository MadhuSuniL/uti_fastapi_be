from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.patient import PatientData
from app.schemas.final_output import FinalResult
from app.schemas.chat import Messages
from app.services.uti_service import UTIService
from app.services.chat_service import ChatService

# Initialize FastAPI app
app = FastAPI(
    title="UTI Antibiotic Recommendation API",
    description="Predicts bacteria type and recommends antibiotics for UTI patients",
    version="1.0.0"
)

origins = [
    "http://localhost:8080",  # Your frontend
    "http://127.0.0.1:8080",  # Sometimes React uses this
    # You can add more origins here if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,         
    allow_methods=["*"],            
    allow_headers=["*"],            
)

# Initialize the service (loads models once)
uti_service = UTIService()


@app.get("/")
def health_check():
    return {"status": "UP", "message": "UTI Antibiotic Recommendation API is running."}


@app.post("/predict", response_model=FinalResult)
def predict_antibiotics(patient: PatientData):
    """
    Predict bacteria and recommend top antibiotics.
    Input: JSON payload of patient clinical data
    Output: JSON with predicted bacteria, resistance, sensitivity, and recommended antibiotics
    """
    try:
        # Convert Pydantic model to dict
        patient_dict = patient.model_dump()
        
        # Run inference through your engine/service
        result = uti_service.generate_final_output(patient_dict)

        print("Prediction Result:", result)  # Debugging statement
        
        return result
            
    except Exception as e:
        raise e

@app.post("/chat", response_model=Messages)
def chat(messages: Messages):
    chat_service = ChatService()
    return chat_service.generate_response(messages.messages)