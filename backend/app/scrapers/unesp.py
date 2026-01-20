from .base import BaseScraper, Job
from playwright.async_api import async_playwright
from typing import List

class UnespScraper(BaseScraper):
    universidade = "UNESP"
    url = "https://inscricoes.unesp.br/concurso/inscricao-aberta"

    async def fetch_jobs(self) -> List[Job]:
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                
                # Wait for Angular SPA to render content
                await page.wait_for_timeout(5000)
                
                # The page shows job listings as blocks with campus headers
                # Look for any container with job info
                await page.wait_for_selector("body", timeout=10000)
                
                # Get page content and parse it
                content = await page.content()
                
                # Find all job blocks - they have edital info and campus
                # Each job has: Campus name, Edital number, description
                job_blocks = await page.query_selector_all("div:has(h3), div:has(h4), article, .card")
                
                if not job_blocks:
                    # Alternative: look for any structured content
                    job_blocks = await page.query_selector_all("main > div > div")
                
                seen_titles = set()
                
                for block in job_blocks:
                    try:
                        text = await block.inner_text()
                        
                        # Check if this looks like a job posting
                        if "Edital" in text or "PROFESSOR" in text.upper() or "concurso" in text.lower():
                            # Get title/campus
                            h_el = await block.query_selector("h3, h4, h5, strong")
                            if h_el:
                                titulo = await h_el.inner_text()
                            else:
                                titulo = text[:100]
                            
                            # Skip duplicates
                            if titulo in seen_titles:
                                continue
                            seen_titles.add(titulo)
                            
                            # Get link if available
                            link_el = await block.query_selector("a")
                            link = self.url
                            if link_el:
                                href = await link_el.get_attribute("href")
                                if href and not href.startswith("javascript"):
                                    link = href if href.startswith("http") else f"https://inscricoes.unesp.br{href}"
                            
                            if titulo.strip() and len(titulo.strip()) > 10:
                                jobs.append(Job(
                                    universidade=self.universidade,
                                    titulo=titulo.strip()[:200],
                                    area=None,
                                    link=link,
                                    status="aberto"
                                ))
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"Unesp scraper error: {e}")
            finally:
                await browser.close()
                
        return jobs
