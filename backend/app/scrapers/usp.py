from .base import BaseScraper, Job
from playwright.async_api import async_playwright
from typing import List

class UspScraper(BaseScraper):
    universidade = "USP"
    url = "https://uspdigital.usp.br/gr/admissao"

    async def fetch_jobs(self) -> List[Job]:
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                
                # Wait for the form to be ready
                await page.wait_for_selector("#inscricao-sitcon", timeout=30000)
                
                # Click "Buscar" button - try multiple selectors
                buscar_btn = page.locator("button").filter(has_text="Buscar").first
                await buscar_btn.click(timeout=10000)
                
                # Wait for tab switch and table to load
                await page.wait_for_timeout(3000)
                
                # Try to find the grid table
                await page.wait_for_selector("table tbody tr", timeout=30000)
                
                # Extract data from the table
                rows = await page.query_selector_all("table tbody tr")
                
                for row in rows:
                    cells = await row.query_selector_all("td")
                    if len(cells) >= 4:
                        titulo = await cells[0].inner_text()
                        link_el = await cells[0].query_selector("a")
                        link = await link_el.get_attribute("href") if link_el else self.url
                        if link and not link.startswith("http"):
                            link = f"https://uspdigital.usp.br{link}"
                        
                        departamento = await cells[3].inner_text() if len(cells) > 3 else ""
                        unidade = await cells[4].inner_text() if len(cells) > 4 else ""
                        periodo = await cells[5].inner_text() if len(cells) > 5 else ""
                        
                        if titulo.strip():
                            jobs.append(Job(
                                universidade=self.universidade,
                                titulo=titulo.strip(),
                                area=departamento.strip() if departamento else None,
                                link=link if link else self.url,
                                data_publicacao=periodo.strip() if periodo else None,
                                status="Inscrições Abertas"
                            ))
                        
            except Exception as e:
                print(f"USP scraper error: {e}")
            finally:
                await browser.close()
                
        return jobs
