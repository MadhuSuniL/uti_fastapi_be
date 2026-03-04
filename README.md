# 🧬 UTI Antibiotic AI – FastAPI Service

## 📌 Overview

**UTI Antibiotic AI** is an AI-powered Clinical Decision Support System designed to predict:

1. 🦠 Bacteria Type
2. 💊 Antibiotic Resistance
3. ✅ Antibiotic Sensitivity
4. 🏆 Ranked Personalized Antibiotic Recommendations

The system uses structured clinical data, machine learning models, and generative AI to assist in evidence-based antibiotic decision-making.

> ⚠️ Disclaimer: This project is developed for academic and research purposes only. It is NOT intended for direct clinical use.

---

# 🏗️ Project Architecture

## 🔄 6-Step ML Pipeline

1. **Patient Clinical Data Collection**
   Structured demographics, lab values, clinical history

2. **Bacteria Prediction (Model 1)**
   Predicts the most likely bacterial pathogen

3. **Resistance Prediction (Model 2)**
   Identifies antibiotics the bacteria is resistant to

4. **Sensitivity Prediction (Model 3)**
   Identifies antibiotics the bacteria is sensitive to

5. **Ranked Recommendation Engine**
   Generates prioritized antibiotic recommendations

6. **Clinical Summary + AI Chat**
   Generates markdown clinical explanation using Generative AI

---

# 📂 Project Structure

```
uti_fastapi/
│
├── app/
│   ├── data/                # Notebooks & datasets
│   ├── inference/           # Model inference logic
│   ├── models/              # Trained ML models (.pkl)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic layer
│   ├── utils/               # Preprocessing & prompt utilities
│   ├── config.py            # App configuration
│   └── main.py              # FastAPI entry point
│
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
└── README.md
```

---

# 🧠 Machine Learning Models

### 🦠 Model 1 – Bacteria Type Prediction

* Input: Structured clinical features
* Output: Predicted bacterial pathogen

### 💊 Model 2 – Antibiotic Resistance Prediction

* Multi-label classification
* Uses ML + MultiLabelBinarizer

### ✅ Model 3 – Antibiotic Sensitivity Prediction

* Predicts sensitive antibiotics
* Used for final ranking logic

---

# 🤖 Technologies Used

* FastAPI
* Scikit-learn
* Pandas / NumPy
* Pydantic
* Generative AI (LLM integration)
* Structured Clinical Data Modeling
* Predictive Analytics

---

# 🚀 Local Development Setup

## 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd uti_fastapi
```

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_key_here
ENV=development
```

Update `config.py` if additional variables are required.

---

## 5️⃣ Run FastAPI Server

From root directory:

```bash
uvicorn app.main:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

---

# 📖 API Documentation

FastAPI automatically generates Swagger documentation:

* Swagger UI:
  `http://127.0.0.1:8000/docs`

* ReDoc:
  `http://127.0.0.1:8000/redoc`

---

# 🧪 How to Test the API

1. Open `/docs`
2. Select the prediction endpoint
3. Provide patient structured clinical data
4. Execute request
5. Review:

   * Predicted Bacteria
   * Resistant Antibiotics
   * Sensitive Antibiotics
   * Ranked Recommendations
   * AI Clinical Summary

---

# 🏥 Example Input Categories

### Demographics

* Age
* Gender
* Department

### Clinical Features

* Chief complaints
* Comorbidities
* Risk factors
* Surgical history
* Social history
* Diagnosis

### Lab Values

* WBC
* CRP
* Serum Creatinine
* Blood Urea
* RBC
* Protein levels
* And more...

### Previous Antibiotic Usage

Multi-select antibiotic history input

---

# 🧩 Core Service Layers

### `uti_service.py`

Handles:

* ML pipeline orchestration
* Model execution
* Ranking logic

### `llm_service.py`

Handles:

* Generative AI integration
* Clinical explanation generation

### `chat_service.py`

Handles:

* Interactive clinical Q&A

---

# 🔐 Production Notes

For deployment:

* Use `gunicorn` with `uvicorn.workers.UvicornWorker`
* Store models securely
* Use environment-based config
* Add authentication layer (recommended)
* Add request validation & logging

---

# 📊 Model Performance (Academic Evaluation)

* Accuracy: ~94.2%
* 50+ Pathogens modeled
* 30+ Antibiotics evaluated

---

# 👨‍⚕️ Clinical Intent

This system aims to:

* Reduce empirical antibiotic misuse
* Improve evidence-based prescription
* Assist early-stage clinical decision support
* Demonstrate ML + GenAI integration in healthcare

---

# 📌 Future Improvements

* Model retraining pipeline
* Real-time hospital data integration
* Audit logging
* Role-based access control
* Explainable AI (SHAP integration)
* Docker containerization
* CI/CD pipeline

---

# 📜 License

Academic Project – Internal Use Only

---

# 🙌 Contributors

Developed as part of AI + Healthcare Research Initiative (2026)

---

## ✅ Conclusion

UTI Antibiotic AI demonstrates how structured clinical data, machine learning, and generative AI can be combined to build an intelligent antibiotic recommendation system using FastAPI.

It is modular, scalable, and designed with clean service-layer architecture to support future production-grade enhancements.
