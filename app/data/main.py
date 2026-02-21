from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.patient import PatientData
from app.services.uti_service import UTIService

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
    allow_origins=origins,          # Which domains can access
    allow_credentials=True,         # Allow cookies, authorization headers
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],            # Allow all headers
)

# Initialize the service (loads models once)
uti_service = UTIService()


@app.get("/")
def health_check():
    return {"status": "UP", "message": "UTI Antibiotic Recommendation API is running."}

@app.get("/metadata")
def get_metadata():
    return uti_service.get_feature_metadata()

@app.post("/predict")
def predict_antibiotics(patient: PatientData):
    """
    Predict bacteria and recommend top antibiotics.
    Input: JSON payload of patient clinical data
    Output: JSON with predicted bacteria, resistance probabilities, and top antibiotics
    """
    try:
        result = uti_service.predict(patient.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
