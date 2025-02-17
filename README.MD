# Testare magazin online

 - Acest proiect conține o suită de teste automatizate pentru validarea funcționalităților unui magazin online. 
Testele sunt implementate folosind Selenium WebDriver și pytest, verificând procesul de căutare a produselor, 
adăugarea în coș, aplicarea reducerilor și finalizarea comenzii.

## Structura proiect

- tests/ - Conține scripturile de testare.
- config.json - Fișier de configurare care stochează detaliile utilizatorilor și URL-ul magazinului.
- conftest.py - Definiția configurației pentru testele pytest.
- helper_functions.py - Funcții reutilizabile pentru testare, cum ar fi căutarea produselor sau completarea formularelor.
- report_log.py - Scriptul principal care rulează testele și generează un raport HTML.
## Cerinte prealabile

- Python 3.x
- Google Chrome si ChromeDriver compatibil cu versiunea browser-ului
- Bibliotecile Python necesare, instalate folosind comanda `pip install -r requirements.txt`

## Pasii pentru rulare

1. **Clonează repository-ul pe mașina locală:**


2. **Instalează dependențele:**

   - pip install -r requirements.txt

3. Execută testele folosind pytest:
   pytest report_log.py -vs -rf --html-report=./test_results.html - va genera un raport html cu rezultatele testelor
   - trebuie sa fii in directorul tests pentru a rula comanda (de rulat cd tests inainte de a rula comanda)
