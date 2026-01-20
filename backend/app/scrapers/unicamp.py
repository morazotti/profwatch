from .base import BaseScraper, Job
from playwright.async_api import async_playwright
from typing import List
import re

class UnicampScraper(BaseScraper):
    universidade = "UNICAMP"
    url = "https://www.sg.unicamp.br/concursos/abertos"

    async def fetch_jobs(self) -> List[Job]:
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                
                # Wait for content to load - look for the main content area
                await page.wait_for_selector("h3, .concurso, article", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Find all h3 elements which are institute names
                h3_elements = await page.query_selector_all("h3")
                
                for h3 in h3_elements:
                    try:
                        unidade = await h3.inner_text()
                        
                        # Get parent block to extract related info
                        parent = await h3.evaluate_handle("el => el.closest('.row') || el.parentElement")
                        
                        # Get area info
                        area = ""
                        area_el = await parent.query_selector("text=/Área/")
                        if area_el:
                            area_text = await area_el.evaluate("el => el.parentElement.textContent || el.textContent")
                            area_match = re.search(r"Área\s*\(s\)?:\s*(.+?)(?=\n|$|Disciplina)", area_text)
                            if area_match:
                                area = area_match.group(1).strip()
                        
                        # Get inscription period
                        inscricao = ""
                        insc_el = await parent.query_selector("text=/Inscrições/")
                        if insc_el:
                            inscricao = await insc_el.evaluate("el => el.parentElement.textContent || el.textContent")
                        
                        if unidade.strip():
                            jobs.append(Job(
                                universidade=self.universidade,
                                titulo=f"Concurso Docente - {unidade.strip()}",
                                area=area if area else None,
                                link=self.url,
                                instrucoes="Acesse sg.unicamp.br/concursos/abertos → Localize o instituto/faculdade → Clique em 'Editais e documentos'",
                                data_publicacao=inscricao.strip()[:100] if inscricao else None,
                                status="aberto"
                            ))
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"Unicamp scraper error: {e}")
            finally:
                await browser.close()
                
        return jobs
