# AgriCare downloads

The download page for the AgriCare apps (Farmer, Admin and Developer), a
capstone project for Suarez Farm, Pandi, Bulacan (STI College San Jose Del
Monte).

**Site:** https://agricare-suarez.vercel.app/

The page is one `index.html`, hosted on Vercel, which publishes it again on
every push to `main`. Its old address on GitHub Pages
(https://jrobinson8756-sketch.github.io/agricare-downloads/) and the address
Vercel gave first (https://agricare-umber.vercel.app/) forward there, so keep
GitHub Pages on and keep both Vercel domains: QR codes and links shared
before still use them. The download buttons point to the newest release's
files:

| App | File |
|-----|------|
| AgriCare Farmer | `agricare-farmer.apk` |
| AgriCare Admin | `agricare-admin.apk` |
| AgriCare Developer | `agricare-developer.apk` |

The app's source code is in a separate, private repository.

## Publishing an update

1. Build the three APKs from the app repository (`.\tool\build_apks.ps1`,
   without `-Demo`) on a PC that has `android\key.properties` and the
   AgriCare release key. Without them the build warns "signed with the
   DEBUG key": such APKs won't install over the apps already on farmers'
   phones, so don't publish them.
2. Check each APK's signer before publishing. Expected: `CN=AgriCare`.
   ```
   apksigner verify --print-certs build\app\outputs\flutter-apk\app-farmer-release.apk
   ```
   (`apksigner` is in the Android SDK's `build-tools` folder; repeat for
   `app-admin-release.apk` and `app-developer-release.apk`.)
3. Rename the three files to the names in the table above
   (`app-farmer-release.apk` → `agricare-farmer.apk`, and so on).
4. Here on GitHub: Releases → Draft a new release → a new tag (e.g.
   `v1.0.1`) → attach the three renamed APKs → Publish release.

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
