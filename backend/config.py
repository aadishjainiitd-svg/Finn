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


# Mock portfolio: 18 NSE companies across sectors and sizes (approximate
# market-capitalisation band, for demo context only).
PORTFOLIO_PROFILE = {
    'RELIANCE': 'Energy & telecom · Large cap', 'HDFCBANK': 'Private bank · Large cap',
    'ICICIBANK': 'Private bank · Large cap', 'TCS': 'IT services · Large cap', 'INFY': 'IT services · Large cap',
    'LT': 'Engineering & construction · Large cap', 'ULTRACEMCO': 'Cement · Large cap',
    'SUNPHARMA': 'Pharmaceuticals · Large cap', 'MARUTI': 'Automobiles · Large cap',
    'TITAN': 'Jewellery & watches · Large cap', 'BAJFINANCE': 'Consumer finance (NBFC) · Large cap',
    'ASIANPAINT': 'Paints · Large cap', 'DIXON': 'Electronics manufacturing · Mid cap',
    'POLYCAB': 'Cables & wires · Mid cap', 'PERSISTENT': 'IT services · Mid cap',
    'TATAPOWER': 'Power utility · Large cap', 'KPITTECH': 'Automotive software · Mid cap',
    'CDSL': 'Market infrastructure · Small cap',
}
# Ad-hoc research set: companies outside the portfolio used to demo on-demand
# research. The engine is not limited to these; any NSE ticker works.
RESEARCH_SET = [
    {'symbol': 'ABB', 'name': 'ABB India', 'sector': 'Electrical equipment', 'why': 'Calendar-year reporter with five years of statements'},
    {'symbol': 'HAVELLS', 'name': 'Havells India', 'sector': 'Consumer electricals', 'why': 'Segment mix across six businesses'},
    {'symbol': 'ASTRAL', 'name': 'Astral', 'sector': 'Pipes & paints', 'why': 'Explicit margin guidance on its calls'},
    {'symbol': 'CROMPTON', 'name': 'Crompton Greaves Consumer', 'sector': 'Fans & appliances', 'why': 'Unfamiliar company; tests the generic pipeline'},
]
