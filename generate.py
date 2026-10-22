import os
from groq import Groq
from dotenv import load_dotenv
from retrieve import retrieve

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_answer(question: str, uploaded_text: str = None, top_k: int = 3, max_new_tokens: int = 150, temperature: float = 0.7):
    try:
        sources = []
        context = ""

        # 1. If the user uploaded a book, use that text!
        if uploaded_text:
            context = uploaded_text[:3000]
            sources.append({"book_id": "Uploaded Document", "page": "N/A", "chunk_id": "N/A"})
        else:
            # 2. Otherwise, search the local 15+ books
            passages = retrieve(question, top_k)
            
            if not passages:
                # POLITE RESPONSE when no books are found
                polite_msg = "I apologize, but I couldn't find any relevant information about that in the provided textbooks. Please try asking a different Computer Science question, or upload a custom PDF in the sidebar."
                return {"answer": polite_msg, "sources": [], "insufficient_evidence": False}

            context = "\n".join([p['text'] for p in passages])
            
            for p in passages:
                clean_book_id = p['chunk_id'].split("_P")[0]
                sources.append({
                    "book_id": clean_book_id,
                    "page": int(p['page']),
                    "chunk_id": p['chunk_id']
                })
        
        # 3. Polite Prompt
        polite_prompt = f"""You are a helpful and polite Computer Science Assistant.
Use the following context from the Computer Science books to answer the question. 

If the answer is missing from the context, DO NOT say "I don't know". Instead, politely explain that the provided textbooks do not contain that specific information, and suggest they try asking a different Computer Science question or uploading a relevant PDF. 

Context:
{context}

Question: {question}
"""
        
        # 4. Call Groq API
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": polite_prompt}],
            model="openai/gpt-oss-20b", 
        )
        
        answer_text = res.choices[0].message.content

        return {
            "answer": answer_text,
            "sources": sources,
            "insufficient_evidence": False
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "sources": [], "insufficient_evidence": True}