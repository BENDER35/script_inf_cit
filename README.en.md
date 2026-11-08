# Cita Previa Audit (SEPE and CC. AA.)

## Description
Automated audit of the employment office appointment (cita previa) system (SEPE and Autonomous Communities' Education/Employment Ministries). It analyzes security CSP headers (frame-ancestors), X-Frame-Options and the architecture of the autonomous portals (iframes vs. direct links), generating a Markdown report.

## Features
- Detects the minimum browser required to load the cita previa pages (modern versions of Chrome, Firefox, Edge, Safari).
- Shows on screen if the audit completed successfully or if there are warnings/errors.
- Checks hardware compatibility with Windows 11 (64-bit architecture, CPU cores, RAM memory, TPM 2.0, Secure Boot).
- If not compatible with Windows 11, suggests Linux alternatives (Ubuntu, openSUSE, Debian, Fedora) to be able to view the web appointment page, either in virtual machines or with dual-boot.
- Compatible with Linux and Windows operating systems (the script runs in any environment with Python 3).
- Supports all 17 Spanish Autonomous Communities.
- Command-line options: --quiet, --browser-detect, --proxy, -o/--output.
- Detects installed browsers and compares with minimum required versions.
- **Managing cita previa in the Community of Madrid**: The script detects if the Madrid portal uses iframe authorized by CSP or direct link, and provides bypass links if necessary.

## Usage
Run the script from the terminal:
```bash
python3 auditar_cita_previa.py [output_file.md]
```
If no output file is provided, it will generate `informe_estado_cita_previa.md` in the same directory.

### Available options:
- -q, --quiet: Silent mode (only critical errors)
- -b, --browser-detect: Check installed browsers against requirements
- -p, --proxy: HTTP proxy URL (e.g., http://127.0.0.1:8080)
- -o, --output: Output markdown file path
- -v, --version: Show version

## Results Interpretation
- The Markdown report includes the state of CSP headers, iframe or direct link implementation in each autonomous portal (all 17 CC.AA.), and technical diagnosis.
- Console messages indicate the minimum recommended browser, overall status, and Windows 11 compatibility.
- **For the Community of Madrid**: If the report indicates that the iframe is blocked by CSP, it is recommended to use the direct bypass links that appear in section 4 of the report, or access directly at https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
- If the hardware is not compatible with Windows 11, consider installing Linux in virtual machines (VirtualBox, VMware) or dual-boot to access the appointment pages.

## Useful Links
- [SEPE](https://sede.sepe.gob.es)
- Included autonomous portals in the audit.
- **Community of Madrid**: https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo
  - Direct bypass link: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
