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
                args=[
                    "--ignore-certificate-errors",
                    "--disable-blink-features=AutomationControlled",
                ]
            )
            context = await browser.new_context(
                ignore_https_errors=True,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                await page.goto(self.url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_load_state("networkidle", timeout=30000)
                await page.wait_for_timeout(5000)
                
                # Check if menu functions are available
                menu_available = await page.evaluate("typeof menu === 'function'")
                
                if menu_available:
                    print("UFSCar: menu function available")
                    
                    # Navigate to Em Andamento > Professor Efetivo
                    await page.evaluate("menu(2)")
                    await page.wait_for_timeout(1000)
                    await page.evaluate("submenu(2, 1)")
                    await page.wait_for_timeout(2000)
                    
                    # For each campus
                    for idx in range(len(self.CAMPUSES)):
                        try:
                            await page.evaluate(f"""
                                (() => {{
                                    const radios = document.querySelectorAll('input[type="radio"][name="campus"]');
                                    if (radios.length > {idx}) {{
                                        radios[{idx}].click();
                                        // Try to submit form
                                        const form = radios[{idx}].closest('form');
                                        if (form) form.submit();
                                    }}
                                }})()
                            """)
                            await page.wait_for_timeout(3000)
                            jobs.extend(await self._extract_jobs(page, self.CAMPUSES[idx]))
                        except Exception:
                            continue
                else:
                    print("UFSCar: menu function NOT available, using clicks")
                    
                    # Click on "Em Andamento" link directly
                    try:
                        await page.click("text=Em Andamento", timeout=5000)
                        await page.wait_for_timeout(1000)
                        await page.click("text=Professor Efetivo", timeout=5000)
                        await page.wait_for_timeout(2000)
                        
                        # Click first campus radio
                        radios = await page.query_selector_all("input[type='radio']")
                        if radios:
                            await radios[0].click()
                            await page.wait_for_timeout(2000)
                            jobs.extend(await self._extract_jobs(page, "São Carlos"))
                    except Exception as e:
                        print(f"UFSCar click navigation failed: {e}")
                
                print(f"UFSCar: Found {len(jobs)} jobs")
                        
            except Exception as e:
                print(f"UFSCar scraper error: {e}")
            finally:
                await browser.close()
                
        return jobs
    
    async def _extract_jobs(self, page, campus: str) -> List[Job]:
        """Extract job listings from the current page."""
        jobs = []
        
        try:
            rows_data = await page.evaluate("""
                (() => {
                    // Find table with job data
                    const tables = document.querySelectorAll('table');
                    for (let table of tables) {
                        const text = table.textContent;
                        if (text.includes('Código') && text.includes('Departamento')) {
                            const rows = Array.from(table.querySelectorAll('tr')).slice(1); // Skip header
                            return rows.map(row => {
                                const cells = row.querySelectorAll('td');
                                if (cells.length < 3) return null;
                                
                                const link = row.querySelector('a');
                                const href = link ? link.getAttribute('href') || '' : '';
                                const match = href.match(/concurso\\((\\d+)\\)/);
                                
                                return {
                                    codigo: cells[0]?.innerText?.trim() || '',
                                    departamento: cells[1]?.innerText?.trim() || '',
                                    classe: cells[2]?.innerText?.trim() || '',
                                    area: cells[3]?.innerText?.trim() || '',
                                    jobId: match ? match[1] : null
                                };
                            }).filter(r => r && r.codigo && !r.codigo.includes('Código') && !r.codigo.includes('Próximos') && !r.departamento.includes('Home'));
                        }
                    }
                    return [];
                })()
            """)
            
            for row in rows_data:
                title = f"{row['classe']} - {row['departamento']} ({campus})"
                # Always use base URL - detail links have SSL issues
                link = self.url
                
                jobs.append(Job(
                    universidade=self.universidade,
                    titulo=title,
                    area=row.get('area') if row.get('area') else None,
                    link=link,
                    instrucoes=f"Acesse concursos.ufscar.br → Em Andamento → Professor Efetivo/Substituto → Selecione campus '{campus}'",
                    status="Em Andamento"
                ))
        except Exception:
            pass
            
        return jobs
