from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
from pathlib import Path
from .scrapers import SCRAPERS
from .scrapers.base import Job
from apscheduler.schedulers.background import BackgroundScheduler

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent

app = FastAPI(title="ProfWatch - Monitoramento de Concursos")

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Cache for scraped jobs
_jobs_cache = []

async def scrape_all():
    """Scrape all universities and return job listings."""
    global _jobs_cache
    results = []
    for scraper in SCRAPERS:
        try:
            jobs = await scraper.fetch_jobs()
            results.extend(jobs)
        except Exception as e:
            print(f"Erro ao buscar {scraper.universidade}: {e}")
    _jobs_cache = results
    return results

@app.get("/")
async def index():
    """Serve the main page."""
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/scrape")
async def scrape_now():
    """Return cached jobs or scrape if cache is empty."""
    if _jobs_cache:
        return _jobs_cache
    return await scrape_all()

@app.get("/refresh")
async def refresh_jobs():
    """Force a new scrape and update cache."""
    return await scrape_all()

def start_scheduler():
    """Schedule periodic scraping every 24 hours."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(scrape_all()), "interval", hours=24)
    scheduler.start()

@app.on_event("startup")
async def startup_event():
    """Run initial scrape on startup."""
    initial_results = await scrape_all()
    print(f"Scraping inicial retornou {len(initial_results)} concursos")
    start_scheduler()
