from .base import BaseScraper, Job
from playwright.async_api import async_playwright
from typing import List

class UfscarScraper(BaseScraper):
    universidade = "UFSCar"
    url = "https://www.concursos.ufscar.br/"
    
    CAMPUSES = ["São Carlos", "Araras", "Sorocaba", "Lagoa do Sino"]

    async def fetch_jobs(self) -> List[Job]:
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--ignore-certificate-errors"]
            )
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            
            try:
                await page.goto(self.url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(2000)
                
                # Navigate to Em Andamento > Professor Efetivo
                # The menu uses JavaScript, so click on text
                andamento_link = page.locator("a").filter(has_text="Em Andamento").first
                await andamento_link.click(timeout=10000)
                await page.wait_for_timeout(1000)
                
                # Click on Professor Efetivo
                efetivo_link = page.locator("a").filter(has_text="Professor Efetivo").first
                await efetivo_link.click(timeout=10000)
                await page.wait_for_timeout(1000)
                
                # For each campus
                for campus in self.CAMPUSES:
                    try:
                        campus_link = page.locator("a, span").filter(has_text=campus).first
                        if await campus_link.count() > 0:
                            await campus_link.click(timeout=5000)
                            await page.wait_for_timeout(2000)
                            
                            # Extract jobs from table
                            jobs.extend(await self._extract_jobs_from_table(page, campus))
                    except Exception:
                        continue
                
                # Also try Professor Substituto
                try:
                    await page.goto(self.url, timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    andamento_link = page.locator("a").filter(has_text="Em Andamento").first
                    await andamento_link.click(timeout=10000)
                    await page.wait_for_timeout(1000)
                    
                    subst_link = page.locator("a").filter(has_text="Professor Substituto").first
                    if await subst_link.count() > 0:
                        await subst_link.click(timeout=10000)
                        await page.wait_for_timeout(2000)
                        
                        for campus in self.CAMPUSES:
                            try:
                                campus_link = page.locator("a, span").filter(has_text=campus).first
                                if await campus_link.count() > 0:
                                    await campus_link.click(timeout=5000)
                                    await page.wait_for_timeout(2000)
                                    jobs.extend(await self._extract_jobs_from_table(page, campus))
                            except Exception:
                                continue
                except Exception:
                    pass
                        
            except Exception as e:
                print(f"UFSCar scraper error: {e}")
            finally:
                await browser.close()
                
        return jobs
    
    async def _extract_jobs_from_table(self, page, campus: str) -> List[Job]:
        """Extract job listings from the currently displayed table."""
        jobs = []
        
        try:
            rows = await page.query_selector_all("table tr")
            
            for row in rows:
                cells = await row.query_selector_all("td")
                if len(cells) >= 3:
                    codigo = await cells[0].inner_text()
                    departamento = await cells[1].inner_text() if len(cells) > 1 else ""
                    classe = await cells[2].inner_text() if len(cells) > 2 else ""
                    area = await cells[3].inner_text() if len(cells) > 3 else ""
                    
                    # Skip header rows or empty
                    if not codigo.strip() or "Código" in codigo:
                        continue
                    
                    jobs.append(Job(
                        universidade=self.universidade,
                        titulo=f"{classe.strip()} - {departamento.strip()} ({campus})",
                        area=area.strip() if area.strip() else None,
                        link=self.url,
                        status="Em Andamento"
                    ))
        except Exception:
            pass
            
        return jobs
