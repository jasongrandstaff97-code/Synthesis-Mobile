import os, asyncio, logging, base64, requests, time, json
from quart import Quart, request, jsonify, render_template_string
from google import genai
from google.genai import types
from groq import Groq
from pinecone import Pinecone
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from hypercorn.config import Config
from hypercorn.asyncio import serve

# --- PATH CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

load_dotenv()
logging.basicConfig(level=logging.INFO)
app = Quart(__name__, template_folder=TEMPLATE_DIR)
executor = ThreadPoolExecutor(max_workers=10)

# --- KEYS (SAFE MODE: No Real Keys Here) ---
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
NEWSDATA_KEY = os.getenv("NEWSDATA_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
pc_index = None
if PINECONE_KEY:
    try: pc_index = Pinecone(api_key=PINECONE_KEY).Index("synthesis-memory")
    except: pass

# --- FUNCTIONS ---
def get_embedding(text):
    if not gemini_client: return None
    try: return gemini_client.models.embed_content(model="text-embedding-004", contents=text).embeddings[0].values
    except: return None

def retrieve_memory(text):
    if not pc_index: return ""
    try:
        res = pc_index.query(vector=get_embedding(text), top_k=2, include_metadata=True)
        mems = [f"PAST: {m['metadata']['text']}" for m in res['matches'] if m['score'] > 0.75]
        return "\nMEMORY:\n" + "\n".join(mems) if mems else ""
    except: return ""

def save_memory(text, verdict):
    if not pc_index: return
    try: pc_index.upsert(vectors=[{"id": str(int(time.time())), "values": get_embedding(text), "metadata": {"text": verdict[:1000]}}])
    except: pass

def get_news(q):
    if not NEWSDATA_KEY: return ""
    try:
        kw = q.split()[0] if q else "tech"
        r = requests.get(f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q={kw}&language=en", timeout=3).json()
        results = r.get('results', [])
        return "NEWS:\n" + "\n".join([t['title'] for t in results[:3]]) if results else "No News Found."
    except: return "News Error"

def run_agent(model, sys, user_prompt, img=None):
    if "gemini" in model:
        if not gemini_client: return "Offline"
        c = [f"{sys}\n{user_prompt}"]
        if img: c.append(img)
        try: return gemini_client.models.generate_content(model=model, contents=c).text
        except Exception as e: return str(e)
    else:
        if not groq_client: return "Offline"
        try: return groq_client.chat.completions.create(model=model, messages=[{"role":"system","content":sys},{"role":"user","content":user_prompt}]).choices[0].message.content
        except Exception as e: return str(e)

@app.route('/')
async def home():
    try: return await render_template_string(open(os.path.join(TEMPLATE_DIR, "index.html")).read())
    except Exception as e: return f"Error: {e}"

@app.route('/api/v6/synthesis', methods=['POST'])
async def synthesize():
    d = await request.get_json()
    p, i = d.get('prompt', ''), d.get('image')
    loop = asyncio.get_running_loop()
    
    g_img = None
    if i and "base64," in i:
        try: g_img = types.Part.from_bytes(data=base64.b64decode(i.split("base64,")[1]), mime_type="image/jpeg")
        except: pass

    news, mem = await asyncio.gather(
        loop.run_in_executor(executor, lambda: get_news(p)),
        loop.run_in_executor(executor, lambda: retrieve_memory(p))
    )
    
    ctx = f"News: {news}\nMemory: {mem}\nUser: {p}"
    
    vis, skep = await asyncio.gather(
        loop.run_in_executor(executor, lambda: run_agent("gemini-2.5-flash", "You are The Visionary (Optimistic).", ctx, g_img)),
        loop.run_in_executor(executor, lambda: run_agent("llama-3.3-70b-versatile", "You are The Skeptic (Critical).", ctx))
    )
    
    judge = await loop.run_in_executor(executor, lambda: run_agent("gemini-2.5-flash", f"You are Juskvi (The Judge). Synthesize a decision.\nQuery: {p}\nVis: {vis}\nSkep: {skep}", ""))
    loop.run_in_executor(executor, lambda: save_memory(p, judge))
    
    return jsonify({"visionary": vis, "skeptic": skep, "final_synthesis": judge})

if __name__ == '__main__':
    config = Config()
    config.bind = ["0.0.0.0:5000"]
    asyncio.run(serve(app, config))
