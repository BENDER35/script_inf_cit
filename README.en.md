# Cita Previa Audit (SEPE and CC. AA.)

## Description
Automated audit of the employment office appointment (cita previa) system (SEPE and Autonomous Communities' Education/Employment Ministries). It analyzes security CSP headers (frame-ancestors), X-Frame-Options and the architecture of the autonomous portals (iframes vs. direct links), generating a Markdown report.

## Features
- Detects the minimum browser required to load the cita previa pages (modern versions of Chrome, Firefox, Edge, Safari).
- Shows on screen if the audit completed successfully or if there are warnings/errors.
- Checks hardware compatibility with Windows 11 (64-bit architecture, CPU cores, RAM memory).
- If not compatible with Windows 11, suggests Linux alternatives (Ubuntu, openSUSE, Debian, Fedora) to be able to view the web appointment page, either in virtual machines or with dual-boot.
- Compatible with Linux and Windows operating systems (the script runs in any environment with Python 3).

## Usage
Run the script from the terminal:
```bash
python3 auditar_cita_previa.py [output_file.md]
```
If no output file is provided, it will generate `informe_estado_cita_previa.md` in the same directory.

## Results Interpretation
- The Markdown report includes the state of CSP headers, iframe or direct link implementation in each autonomous portal, and technical diagnosis.
- Console messages indicate the minimum recommended browser, the overall status, and Windows 11 compatibility.
- If the hardware is not compatible with Windows 11, consider installing Linux in virtual machines (VirtualBox, VMware) or dual-boot to access the appointment pages.

## Useful Links
- [SEPE](https://sede.sepe.gob.es)
- Included autonomous portals in the audit.
