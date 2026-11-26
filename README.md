# Signal Relics

[Explore the collection](https://coolcode.ca/signalrelics/): historical modems, computers, terminals, telephones, exchanges, telegraphs, radio equipment and storage hardware from Science Museum Group.

<!-- coolcode:guide -->
Search the captured collection by object, maker or material, filter overlapping museum date ranges, compare two objects and save a local shortlist. Every object links to its source and every displayed preview retains its individual image licence. The source edition is shown separately from the last successful check.
<!-- /coolcode:guide -->

## Use it

Search any words within the captured collection, choose a category or maker, and refine years. The gallery loads 48 objects at a time; Show more expands it. Inspect shows the original catalogue description, makers, dates and source. Compare keeps two objects side by side. Saved object IDs remain in this browser; CSV exports contain the current filtered selection, including source URLs.

No key or install is required. The shared CoolCode visit counter records visits; search terms, saved IDs and comparison choices are not sent to it. Previews load directly from the museum image host. Clearing browser storage clears saved IDs.

## Sources and coverage

The collector reads the museum's [official bulk exports](https://coimages.sciencemuseumgroup.org.uk/datasets/index.html), avoiding repeated API queries and all IIIF/zoom harvesting. The first source edition is **2025-04-09**. `checkedAt` records our successful retrieval/check, not an updated museum edition. Category membership is a documented title/object-type match, not a claim to be every historical example. Date labels are preserved; absent dates and makers stay unknown. Dated ranges use overlap when filtering.

Title, maker and date metadata are CC0. Descriptions and other text are CC BY 4.0, attributed to **© The Board of Trustees of the Science Museum**, with original-record links. Media rights are evaluated independently for each image. Only recognized CC BY-NC-SA 4.0, CC BY-NC-ND 4.0 or Open Government Licence v3.0 media are displayed. The noncommercial image licences must be respected; do not add commercial reuse without reviewing/removing those images. A thumbnail is not a full-resolution download or permission for other images on the record. Unknown/mixed rights are excluded from previews.

## Expand or customize

Edit `web/config.json`: add any collection ID/label and case-insensitive regular-expression patterns to match object titles and catalogue terms. Update `sourceUrl` and `sourceEdition` together when the museum publishes a newer bulk edition; `minimumSourceRecords` is a safety threshold, not an expected exact count. Filter counts derive from the actual records and accept added groups. The source catalogue is deliberately not queried live by visitors.

Run **Actions → Signal Relics · Check and publish → Run workflow** with **Refresh museum collection** enabled. The workflow downloads one bulk archive, streams it with bounded buffering, validates structure and row coverage, tests/builds, then commits and deploys the small normalized collection. Existing snapshots are retained in Git history. If any validation fails, the previous publication remains available. The first push collects if no saved data exists; later normal pushes build offline. A monthly scheduled refresh checks the configured edition; changing the source edition is explicit so an unexpected upstream file cannot silently change coverage.

Local equivalent: `python3 scripts/collect.py` (or `--input /path/to/official.zip`), review `web/data/objects.json`, then run the checks below and commit the capture. The full museum archive is temporary and never published. The configured archive is about 145 MB; the normalized selection is much smaller.

## Checks and integration

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

CI also checks the built project subpath in Chromium. Source files live in `web/`; `dist/` is generated. The monthly collector is `.github/workflows/pages.yml` (`11 9 8 * *`, UTC), with `workflow_dispatch` available and a separate allowlisted schedule guard. The hub registers its catalogue entry, visit ID, repository audit, schedule and freshness probe `data/objects.json` → `checkedAt`; the pinned museum edition is not used as a freshness clock. No Worker API handler or secret is required.
