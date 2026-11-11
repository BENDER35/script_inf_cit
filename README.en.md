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
- **Detects Windows 10 with ESU ("modo prórroga")** and warns about its expiration date (October 2028), Microsoft Edge ending support the same day, and the failures that may appear afterwards (OpenStreetMap, root certificates, incompatibilities, confirmation SMS, etc.).
- **Cita previa in the Community of Madrid**: the script detects whether the Madrid portal uses a CSP-authorized iframe or a direct link, and offers bypass links if needed.

## Windows 10 with ESU ("modo prórroga")

If the script detects Windows 10 with ESU (Extended Security Updates) installed, it reports that the system **is still supported** and that the employment office appointment service remains **free** in the Autonomous Communities that list the **012** number for requesting an appointment and where the job seeker uses the employment office services.

Under **BOE no. 296 of 10 December 2012**, all Spanish telecommunications operators must charge for the 012 number either **per minute** (the duration of the in-person or semi-presential procedure) or **per access** to the employment offices (each time the job seeker needs to visit them). If the job seeker has no electronic means or insufficient training to use the permanent appointment system, they will need to call citizen attention to generate a slot reservation, which they must present at the employment office; in that case, the charge applies for each access to the offices.

**Important notice:** Windows 10 with an ESU license **is not permanent**. It expires in **October 2028**, the same day Microsoft ends support for Microsoft Edge. After that, over time browsers may experience usability problems, broken page elements, OpenStreetMap failing, root certificate errors, page incompatibility errors, confirmation SMS failures, or any other error that prevents using the page.

If the page fails and talking to the employment office does not help, the job seeker may lose the right to request a free appointment at offices that use the 012 number and manage appointments and attendance by capacity (aforo). Internet fixes such as Legacy Update or Extended Kernel **are not official Microsoft solutions**, are community-made, and may work only partially or not at all, especially the extended kernel. In those cases, installing **Linux** (dual boot or a virtual machine if Windows is still needed) is recommended to recover **free Internet access to the appointment system** of employment offices that list the **012** as the phone number for getting an appointment without needing Internet access. This avoids having to call 012, which under Spanish law is a paid short number.

## Cita previa in the Community of Madrid

The Community of Madrid portal uses an `<iframe>` authorized by the SEPE `frame-ancestors` directive. If the report indicates that the iframe is blocked by CSP or rendering problems appear:

1. Make sure you have an up-to-date browser (Chrome 108+, Firefox 122+, Edge 120+, Safari 15+).
2. Use the direct bypass link: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
3. If the iframe remains blocked, temporarily disable ad-blocking or script-blocking extensions.

See `INFO_OF_EMP_ESP_2026.txt` for more information about employment offices in Spain.

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
- Console messages indicate the minimum recommended browser, overall status, Windows 11 compatibility, and Windows 10 ESU support status.
- If the hardware is not compatible with Windows 11, consider installing Linux in virtual machines (VirtualBox, VMware) or dual-boot to access the appointment pages.

## Useful Links
- [SEPE](https://sede.sepe.gob.es)
- Included autonomous portals in the audit.
- **Community of Madrid**: https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo
  - Direct bypass link: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
