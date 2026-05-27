# empirical_parsers/ - empirical archive loaders

Split from the former `empirical_ingest.py` god-module. Each parser owns one
modality; orchestration lives in `empirical_pipeline.py`.

| Module | Loads |
| --- | --- |
| `panels.py` | Dryad/Figshare odor-response workbooks |
| `calcium.py` | Paoli MATLAB `.mat` archives |
| `waggle.py` | Hadjitofi-Webb Figshare CSVs |
| `antennal.py` | Jernigan antennal movement CSVs |
| `nouvian.py` | Nouvian biogenic-amine sheet heuristics |
| `anatomy_loader.py` | HSB anatomy download JSON + inventories |
| `common.py` | Shared zip/CSV/workbook helpers |

## Boundaries

- No imports from `beestack.visualization` or `run_simulation`.
- Fail loud on corrupt archives; return empty tuples when payloads are absent.
