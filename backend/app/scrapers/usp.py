from .base import BaseScraper, Job
from playwright.async_api import async_playwright
from typing import List

class UspScraper(BaseScraper):
    universidade = "USP"
    url = "https://uspdigital.usp.br/gr/admissao"

    async def fetch_jobs(self) -> List[Job]:
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                ]
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = await context.new_page()
            
            try:
                await page.goto(self.url, timeout=90000, wait_until="commit")
                await page.wait_for_load_state("load", timeout=60000)
                await page.wait_for_timeout(5000)
                
                # Click the Buscar button
                await page.click("button.buscar, .buscar", timeout=30000)
                
                # Wait for the jqGrid table to load
                # The results appear in table.ui-jqgrid-btable with tr.jqgrow rows
                await page.wait_for_selector("tr.jqgrow", timeout=30000)
                await page.wait_for_timeout(3000)
                
                # Extract data from the jqGrid table
                jobs_data = await page.evaluate("""
                    (() => {
                        const table = document.querySelector('.ui-jqgrid-btable, table.pad-inscricao-grid');
                        if (!table) return [];
                        
                        const rows = Array.from(table.querySelectorAll('tr.jqgrow'));
                        return rows.map(row => {
                            const cells = Array.from(row.querySelectorAll('td'));
                            // Column order based on analysis:
                            // 1: Título, 4: Departamento, 5: Unidade, 6: Período, 8: Situação
                            return {
                                titulo: cells[1] ? cells[1].innerText.trim() : '',
                                departamento: cells[4] ? cells[4].innerText.trim() : '',
                                unidade: cells[5] ? cells[5].innerText.trim() : '',
                                periodo: cells[6] ? cells[6].innerText.trim() : '',
                                situacao: cells[8] ? cells[8].innerText.trim() : 'Inscrições Abertas',
                            };
                        }).filter(j => j.titulo && j.titulo.length > 3);
                    })()
                """)
                
                for job_data in jobs_data:
                    area = None
                    if job_data.get('departamento') and job_data.get('unidade'):
                        area = f"{job_data['departamento']} - {job_data['unidade']}"
                    elif job_data.get('departamento'):
                        area = job_data['departamento']
                    elif job_data.get('unidade'):
                        area = job_data['unidade']
                    
                    jobs.append(Job(
                        universidade=self.universidade,
                        titulo=job_data['titulo'],
                        area=area,
                        link=self.url,
                        instrucoes="Acesse uspdigital.usp.br/gr/admissao → Clique em 'Buscar' → Localize o concurso na lista",
                        data_publicacao=job_data.get('periodo'),
                        status=job_data.get('situacao', 'Inscrições Abertas')
                    ))
                
                print(f"USP: Found {len(jobs)} jobs")
                        
            except Exception as e:
                print(f"USP scraper error: {e}")
            finally:
                await browser.close()
                
        return jobs
