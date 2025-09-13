from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "ibm-granite/granite-3.3-2b-instruct"

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    print("✅ Model and tokenizer loaded successfully.")
except Exception as e:
    print("❌ Load failed:", e)
