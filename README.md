# Birthday Star Finder

A single-page web app for browsing the stars within 100 light-years of the Sun. Pick an observatory, a night and an observing window. The table then shows the stars in your distance range that are actually observable from that site during that window.

The whole app is one HTML file with the catalog embedded. It has no server, no build step for users, and no external JavaScript. Open `index.html` in a browser, put it on any static web host, or serve it with GitHub Pages.

## Features

- **Observatory:** 26 major sites (Mount Wilson, Palomar, Maunakea, Las Campanas, Paranal, La Palma, SAAO, Siding Spring and others), or a custom latitude, longitude and time zone.
- **Night:** defaults to tonight in the observatory's own time zone.
- **Observing window:** defaults to the end of evening twilight through the start of morning twilight (civil, nautical or astronomical), and can be edited.
- **Distance range:** a two-handle slider over a histogram of the catalog, plus number fields.
- **Birthday star:** enter a birth date to find stars whose light left them within half a year of your birth.
- **Visibility filters:**
  - minimum altitude (the page shows the matching airmass)
  - maximum hour angle
  - minimum time the star must stay observable
  - magnitude limit
- **Results table:**
  - sortable and searchable
  - coordinates are precessed to the observing date
  - shows maximum altitude, time of highest altitude, and hours observable
  - "Copy table as CSV" exports the current view
- **Star detail:** distance with its error, altitude through the night, transit time, and a SIMBAD link.
- **All-sky map:** shows the matches at any moment in the window, with a time slider and animation.
- **Night-vision mode:** turns the whole page red for use at the telescope.
- **Load another CSV:** switches catalogs in the browser without rebuilding.

## Repository layout

```
index.html                       Built app, ready to serve (generated; do not edit by hand)
src/template.html                App source: HTML, CSS and JavaScript, with /*CSV*/ and /*CATNAME*/ markers
data/Gaia_NS_bright_merge.csv    Star catalog embedded into index.html
tools/build.py                   Embeds a CSV into the template and writes index.html
```

## Building

Edit `src/template.html` or replace the catalog, then rebuild. Python 3.8+ is the only requirement, with no packages.

```sh
python3 tools/build.py                          # default catalog -> index.html
python3 tools/build.py data/other.csv           # a different catalog
python3 tools/build.py data/other.csv -o test.html
```

Commit the regenerated `index.html` along with the source change.

## Publishing with GitHub Pages

1. Push this repository to GitHub.
2. Go to **Settings → Pages**, set the source to **Deploy from a branch**, and choose `main` with the `/ (root)` folder.
3. The app appears at `https://<your-user>.github.io/<repo-name>/` a minute or so later.

## Catalog format

The catalog is a comma-separated file with one header row. Fields that contain commas may be quoted. Column names are matched case-insensitively, and only the first three are required.

| Column | Meaning | Used for |
|---|---|---|
| `RA_ICRS`, `DE_ICRS` | Position in degrees, ICRS, **epoch J2016.0** | Required |
| `Plx` | Parallax in mas | Required; distance = 3261.56 / Plx light-years |
| `e_Plx` | Parallax error in mas | Distance uncertainty |
| `pmRA`, `pmDE` | Proper motion in mas/yr (`pmRA` includes cos δ) | Moving positions to the observing date |
| `Vmag`, `Gmag` | V magnitude, Gaia G magnitude | V is used when present, otherwise G |
| `BP-RP`, `B-V` | Gaia BP−RP, Johnson B−V colour | BP−RP is used when present, otherwise B−V |
| `Name` | Bright Star Catalogue designation, e.g. `9Alp CMa`, `35    Leo` | Shown as `α CMa`, `35 Leo` |
| `HD`, `HIP`, `Source` | Henry Draper, Hipparcos and Gaia DR3 identifiers | Labels, search and SIMBAD links |

The page handles these quirks in the data:

- Stars are labelled by Name, then HD, then HIP, then Gaia DR3 number.
- SIMBAD links use the Gaia DR3 ID, then HIP, then HD.
- `-2147483648` in `HD` and `0.0` in `Name` are treated as blank.
- Rows that are exact duplicates are shown once.
- B−V is converted to an approximate BP−RP only to colour the map dots and to sort the colour column; the table shows the original value and its band.

`PM`, `e_pmRA` and `e_pmDE` are present in the current file but not used.

## How visibility is computed

All calculations run in the browser:

- **Star positions:** each star's J2016.0 position is moved by its proper motion to the middle of the observing window, then precessed to the mean equinox of date using IAU 1976 precession. The table lists these coordinates.
- **Altitude sampling:** altitude is sampled at least every 5 minutes through the window. A moment counts as observable when the star is above the altitude limit and within the hour-angle limit.
- **Sun and Moon:** they use low-precision formulas. Twilight times are good to about a minute. When the Sun never reaches the chosen twilight depth, as at high latitudes in summer, the window falls back to the next shallower twilight.
- **Time zones:** handled with the browser's `Intl` API, so daylight-saving changes are correct for each site.

Limitations:

- Atmospheric refraction is ignored, so stars near the horizon are up to about 0.5° higher than shown.
- Nutation and aberration are not applied. Positions are mean coordinates of date, which differ from true apparent positions by up to about half an arcminute, which is plenty for planning and not enough for pointing a telescope.
- Stars without parallax, and stars beyond the catalog's 100 ly limit (Canopus, Achernar, Hadar and others), are not included.

## Data sources

- **Gaia:** ESA mission *Gaia* (https://www.cosmos.esa.int/gaia), Data Release 3, processed by the Gaia Data Processing and Analysis Consortium (DPAC, https://www.cosmos.esa.int/web/gaia/dpac/consortium). Gaia Collaboration, Vallenari et al. 2023, A&A 674, A1.
- **Bright stars and extra columns:**  The Hipparcos catalogue (ESA 1997; van Leeuwen 2007, A&A 474, 653) for stars too bright for Gaia, the Henry Draper Catalogue for HD numbers, and the Yale Bright Star Catalogue (Hoffleit & Warren 1991) for the `Name` designations.
- **Star lookups:** SIMBAD, CDS, Strasbourg (Wenger et al. 2000, A&AS 143, 9).

## Third-party assets

The page loads three typefaces from Google Fonts: Libre Bodoni, Public Sans and JetBrains Mono, all under the SIL Open Font License. When offline it falls back to system fonts. Nothing else is loaded from the network.

## License

MIT License. Use of the Gaia data requires the above acknowledgement.
