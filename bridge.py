import streamlit as st
import sys
import os
import torch
import tiktoken

# Fix Python path so it can find model.py in this folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model import GPTConfig, GPT

# Setup device
device = 'cuda' if torch.cuda.is_available() else 'cpu'

@st.cache_resource
def load_model():
    print("Loading GPT-2 model into memory (this only happens once)...")
    model = GPT.from_pretrained('gpt2', dict(dropout=0.0))
    model.eval()
    model.to(device)
    enc = tiktoken.get_encoding("gpt2")
    return model, enc

model, enc = load_model()

encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
decode = lambda l: enc.decode(l)

def generate_local_answer(question: str, max_new_tokens=50, temperature=0.7):
    # Format prompt
    prompt = question # We are passing the full formatted prompt from generate.py now
    
    # Encode
    start_ids = encode(prompt)
    x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])
    
    # Generate
    with torch.no_grad():
        y = model.generate(x, max_new_tokens, temperature=temperature, top_k=200)
    
    # Decode
    answer = decode(y[0].tolist())
    
    # Remove the prompt from the generated text so we only see the new words
    answer = answer.replace(prompt, "").strip()
        
    return answer
    # Encode the prompt into a tensor
    start_ids = encode(prompt)
    x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])
    
    # Generate the output
    with torch.no_grad():
        y = model.generate(x, max_new_tokens, temperature=temperature, top_k=200)
    
    # Decode the output back to text
    answer = decode(y[0].tolist())
    
    # Extract the answer part
    if "Answer:" in answer:
        answer = answer.split("Answer:")[1].strip()
        
    return answer