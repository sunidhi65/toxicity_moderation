from fastapi import FastAPI
import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer
import torch
import torch.nn.functional as F
from database import SessionLocal, ModerationResult
from huggingface_hub import hf_hub_download

app = FastAPI()

# -----------------------------------
# Download model from Hugging Face
# -----------------------------------
model_path = hf_hub_download(
    repo_id="sunidhi65/toxicity-model",
    filename="toxicity_model.onnx"
)

# Download ONNX external data file
hf_hub_download(
    repo_id="sunidhi65/toxicity-model",
    filename="toxicity_model.onnx.data"
)

# -----------------------------------
# Load tokenizer
# -----------------------------------

tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased"
)

# -----------------------------------
# Load ONNX model
# -----------------------------------

session = ort.InferenceSession(model_path)

@app.get("/")
def home():
    return {"message": "Toxicity API is running"}

@app.post("/predict")
def predict(text: str):

    # Tokenize input
    inputs = tokenizer(
        text,
        return_tensors="np",
        truncation=True,
        padding="max_length",
        max_length=128
    )

    # Ensure int64 dtype
    input_ids = inputs["input_ids"].astype(np.int64)
    attention_mask = inputs["attention_mask"].astype(np.int64)

    # ONNX inference
    outputs = session.run(
        None,
        {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
    )

    logits = outputs[0]

    # Convert logits -> probabilities
    probs = F.softmax(
        torch.tensor(logits),
        dim=1
    ).numpy()

    toxic_prob = probs[0][1]

    # Threshold
    threshold = 0.7

    prediction = int(toxic_prob > threshold)

    # -----------------------------------
    # Store result in SQLite
    # -----------------------------------

    db = SessionLocal()

    result_entry = ModerationResult(
        text=text,
        prediction="toxic" if prediction == 1 else "safe",
        toxic_probability=float(toxic_prob)
    )

    db.add(result_entry)
    db.commit()
    db.close()

    return {
        "text": text,
        "toxic_probability": float(toxic_prob),
        "prediction": "toxic" if prediction == 1 else "safe"
    }