from .usp import UspScraper
from .unesp import UnespScraper
from .unicamp import UnicampScraper
from .ufscar import UfscarScraper

SCRAPERS = [
    UspScraper(),
    UnespScraper(),
    UnicampScraper(),
    UfscarScraper(),
]
