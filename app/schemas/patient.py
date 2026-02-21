from pydantic import BaseModel
from typing import Optional

class PatientData(BaseModel):
    AGE: float
    GENDER: str
    DEPARTMENT: str
    CHIEF_COMPLAINTS: str
    COMORBIDITIES: Optional[str] = None
    RISKFACTORS: Optional[str] = None
    SURGICAL_HISTORY: Optional[str] = None
    SOCIAL_HISTORY: Optional[str] = None
    DIAGNOSIS: str
    CLASSIFICATION_OF_UTI: str
    TYPE_OF_UTI: str
    SITE_OF_INFECTION: str
    TYPE_OF_SAMPLE: str
    
    CBP_LYMPHOCYTES: float
    WBC: float
    POLYMORPHS: float
    CRP: float
    RFT_SERUM_CREATININE: float
    SERUM_URIC_ACID: float
    BLOOD_UREA: float
    CUE_PUS_CELLS: float
    EPITHELIAL_CELLS: float
    PROTEINS: str  # Changed to string
    RBC: float

    PREVIOUS_ANTIBIOTIC_USED: Optional[str] = None



