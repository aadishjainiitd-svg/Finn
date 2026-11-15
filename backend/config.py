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

# Sample portfolio for demonstration: illustrative weights (sum 100%) and
# one-line theses written as an investor might. Not advice; editable in Book.
SAMPLE_BOOK = {
    'RELIANCE': (9, 'Retail and Jio cash flows fund the new-energy build-out while refining stays cyclical.'),
    'HDFCBANK': (9, 'Deposit franchise rebuilds margins after the merger; credit costs stay low.'),
    'ICICIBANK': (8, 'Best-in-class return on assets with steady retail and SME loan growth.'),
    'TCS': (7, 'Large-deal wins and margin discipline offset a slow discretionary-spend cycle.'),
    'INFY': (6, 'AI-led services demand lifts growth back to high single digits.'),
    'LT': (7, 'Record order book and execution keep revenue growth in the mid-teens.'),
    'ULTRACEMCO': (5, 'Capacity additions and consolidation give pricing power as housing demand grows.'),
    'SUNPHARMA': (5, 'Specialty products in the US grow faster than generics price erosion.'),
    'MARUTI': (5, 'New SUVs and exports recover market share without hurting margins.'),
    'TITAN': (5, 'Jewellery share gains from unorganised players continue despite gold volatility.'),
    'BAJFINANCE': (5, 'Customer franchise compounds loan growth near 25% with contained credit costs.'),
    'ASIANPAINT': (4, 'Brand and distribution defend share against new paint entrants.'),
    'DIXON': (4, 'Mobile manufacturing scale-up under PLI drives earnings growth.'),
    'POLYCAB': (4, 'Wires and cables demand from construction and power capex stays strong.'),
    'PERSISTENT': (4, 'Mid-tier IT winner with industry-leading growth and improving margins.'),
    'TATAPOWER': (5, 'Renewables and rooftop solar shift earnings mix toward regulated, cleaner returns.'),
    'KPITTECH': (4, 'Automotive software spend recovers as carmakers move to software-defined vehicles.'),
    'CDSL': (4, 'Rising demat accounts and market activity grow fee income with high margins.'),
}
