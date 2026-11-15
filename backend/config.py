"""Server-only configuration. Never serialize the environment."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
DATA = Path(os.getenv('FINN_DATA_DIR', str(ROOT / 'data')))
DATA.mkdir(parents=True, exist_ok=True)
MODEL = os.getenv('FINN_LLM_MODEL', 'openai/gpt-oss-120b')
GEMINI_MODEL = os.getenv('FINN_GEMINI_MODEL', 'gemini-3.5-flash-lite')
PORTFOLIO = ['RELIANCE','HDFCBANK','ICICIBANK','TCS','INFY','LT','ULTRACEMCO','SUNPHARMA','MARUTI','TITAN','BAJFINANCE','ASIANPAINT','DIXON','POLYCAB','PERSISTENT','TATAPOWER','KPITTECH','CDSL']
PARSER = 'pdfium-5.15.2-pages-v5-verified-fonts'

