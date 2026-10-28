# AgriCare downloads

The download page for the AgriCare apps (Farmer, Admin and Developer), a
capstone project for Suarez Farm, Pandi, Bulacan (STI College San Jose Del
Monte).

**Site:** https://jrobinson8756-sketch.github.io/agricare-downloads/

The page is one `index.html` served by GitHub Pages. Its download buttons
point to the newest release's files:

| App | File |
|-----|------|
| AgriCare Farmer | `agricare-farmer.apk` |
| AgriCare Admin | `agricare-admin.apk` |
| AgriCare Developer | `agricare-developer.apk` |

The app's source code is in a separate, private repository.

## Publishing an update

1. Build the three APKs from the app repository (`.\tool\build_apks.ps1`,
   without `-Demo`), signed with the AgriCare release key.
2. Here on GitHub: Releases → Draft a new release → a new tag (e.g.
   `v1.0.1`) → attach the three APKs, named exactly as in the table above →
   Publish release.

The page needs no change: its buttons always download the latest release,
and it reads each file's version and size from GitHub when it opens. A file
missing from the release shows "Not available yet".

## Tests

The tests open the page in Google Chrome at a phone's size (it must be
installed):

```
python -m venv .venv
.venv\Scripts\pip install -r tests\requirements.txt
.venv\Scripts\python -m pytest tests -q
```
