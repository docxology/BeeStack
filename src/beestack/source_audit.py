"""Offline source, citation, and conservative-claim audits for BeeStack."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

from .brain import empirical_anatomy_datasets, empirical_brain_datasets
from .visualization.figure_registry import all_figure_narratives

EXPECTED_BIB_DOIS: dict[str, str] = {
    "galizia1999glomerular": "10.1038/8144",
    "rougier2014figures": "10.1371/journal.pcbi.1003833",
    "cleveland1984graphical": "10.1080/01621459.1984.10478080",
    "heer2012interactive": "10.1145/2133806.2133821",
    "ragan2016provenance": "10.1109/TVCG.2015.2467551",
    "crameri2020colour": "10.1038/s41467-020-19160-7",
    "vaxenburg2025flybody": "10.1038/s41586-025-09029-4",
    "becher2014beehave": "10.1111/1365-2664.12222",
    "rybak2010digital": "10.3389/fnsys.2010.00030",
    "brandt2005standardbrain": "10.1002/cne.20644",
    "todorov2012mujoco": "10.1109/IROS.2012.6386109",
    "hadjitofi2024currentbiology": "10.1016/j.cub.2024.02.045",
    "wario2015automatic": "10.3389/fevo.2015.00103",
    "riley2005flightpaths": "10.1038/nature03526",
    "landgraf2011roboticdance": "10.1371/journal.pone.0021354",
    "hateren2019neuroethology": "10.3390/insects10100336",
    "wilkinson2016fair": "10.1038/sdata.2016.18",
    "lamprecht2020fairsoftware": "10.3233/DS-190026",
    "fair4rs2022principles": "10.1038/s41597-022-01710-x",
    "dong2023wagglesocial": "10.1126/science.ade1702",
    "pnas2026waggleaudience": "10.1073/pnas.2518687123",
    "wallberg2019hav31": "10.1186/s12864-019-5642-0",
    "walsh2022hgd": "10.1093/nar/gkab1018",
    "rechlaval2025beebiome": "10.1186/s12859-025-06229-7",
    "dorey2023beebdc": "10.1038/s41597-023-02626-w",
    "vanengelsdorp2009ccd": "10.1371/journal.pone.0006481",
    "scientificreports2026amitraz": "10.1038/s41598-026-44796-8",
}

_FIELD_RE = re.compile(
    r"(?P<field>[A-Za-z][A-Za-z0-9_-]*)\s*=\s*"
    r"(?P<delimiter>[{\"])(?P<value>.*?)(?(delimiter)}|\")\s*,?",
    re.DOTALL,
)
_ENTRY_RE = re.compile(
    r"@(?P<kind>\w+)\s*\{\s*(?P<key>[^,\s]+)\s*,(?P<body>.*?)(?=\n@\w+\s*\{|$)",
    re.DOTALL,
)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
_CITATION_CLUSTER_RE = re.compile(r"\[(?:[^\]]*?@[^]]+?)\]")
_CITATION_KEY_RE = re.compile(r"@([A-Za-z0-9_:-]+)")
_CROSSREF_PREFIXES = ("fig:", "sec:", "eq:", "tbl:")
_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

_UNSAFE_TWIN_WORDS = (
    "complete",
    "finished",
    "ready",
    "validated",
    "calibrated",
    "operational",
    "decision-support",
)
_CONSERVATIVE_TWIN_WORDS = (
    "not",
    "target",
    "readiness",
    "blocker",
    "blocked",
    "missing",
    "requires",
    "until",
    "scaffold",
    "future",
    "governance",
    "uncertainty",
    "residual",
    "assimilation",
    "long-horizon",
    "longitudinal",
)


@dataclass(frozen=True)
class SourceAudit:
    """Source/citation consistency audit result."""

    citation_keys: tuple[str, ...]
    bibliography_keys: tuple[str, ...]
    missing_citation_keys: tuple[str, ...]
    unused_bibliography_keys: tuple[str, ...]
    doi_mismatches: tuple[str, ...]
    missing_required_bib_fields: tuple[str, ...]
    registry_dois_missing: tuple[str, ...]
    registry_dois_represented: tuple[str, ...]
    figure_registry_citation_keys_missing: tuple[str, ...]
    figure_registry_source_dois_missing: tuple[str, ...]
    unconservative_digital_twin_claims: tuple[str, ...]
    malformed_cited_dois: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return not (
            self.missing_citation_keys
            or self.doi_mismatches
            or self.missing_required_bib_fields
            or self.registry_dois_missing
            or self.figure_registry_citation_keys_missing
            or self.figure_registry_source_dois_missing
            or self.unconservative_digital_twin_claims
            or self.malformed_cited_dois
        )

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["passed"] = self.passed
        return payload


def audit_sources(
    project_root: Path,
    *,
    required_bib_dois: Mapping[str, str] | None = None,
    registry_dois: tuple[str, ...] | None = None,
    figure_registry_citation_keys: tuple[str, ...] | None = None,
    figure_registry_source_dois: tuple[str, ...] | None = None,
) -> SourceAudit:
    """Audit manuscript citations, bibliography metadata, and conservative claims."""

    project_root = project_root.resolve()
    manuscript_dir = project_root / "manuscript"
    manuscript_files = tuple(sorted(manuscript_dir.glob("*.md")))
    manuscript_text_by_path = {
        path: path.read_text(encoding="utf-8", errors="replace") for path in manuscript_files
    }
    manuscript_text = "\n".join(manuscript_text_by_path.values())
    bib_entries = parse_bibtex_entries(
        (manuscript_dir / "references.bib").read_text(encoding="utf-8", errors="replace")
        if (manuscript_dir / "references.bib").exists()
        else ""
    )
    citation_keys = extract_pandoc_citation_keys(manuscript_text)
    bibliography_keys = tuple(sorted(bib_entries))
    missing_citation_keys = tuple(key for key in citation_keys if key not in bib_entries)
    unused_bibliography_keys = tuple(key for key in bibliography_keys if key not in citation_keys)
    expected_dois = dict(EXPECTED_BIB_DOIS if required_bib_dois is None else required_bib_dois)
    doi_mismatches = _doi_mismatches(bib_entries, expected_dois)
    missing_required = _missing_required_fields(bib_entries, expected_dois)
    required_registry_dois = (
        registry_dois if registry_dois is not None else _default_registry_dois()
    )
    represented, missing_registry = _registry_doi_coverage(bib_entries, required_registry_dois)
    figure_keys = (
        figure_registry_citation_keys
        if figure_registry_citation_keys is not None
        else _default_figure_registry_citation_keys()
    )
    figure_dois = (
        figure_registry_source_dois
        if figure_registry_source_dois is not None
        else _default_figure_registry_source_dois()
    )
    missing_figure_keys = tuple(
        sorted({key for key in figure_keys if key and key not in bib_entries})
    )
    _, missing_figure_dois = _registry_doi_coverage(bib_entries, figure_dois)
    unsafe_twin_claims = _unconservative_digital_twin_claims(project_root, manuscript_text_by_path)
    return SourceAudit(
        citation_keys=tuple(sorted(set(citation_keys))),
        bibliography_keys=bibliography_keys,
        missing_citation_keys=tuple(sorted(set(missing_citation_keys))),
        unused_bibliography_keys=unused_bibliography_keys,
        doi_mismatches=doi_mismatches,
        missing_required_bib_fields=missing_required,
        registry_dois_missing=missing_registry,
        registry_dois_represented=represented,
        figure_registry_citation_keys_missing=missing_figure_keys,
        figure_registry_source_dois_missing=missing_figure_dois,
        unconservative_digital_twin_claims=unsafe_twin_claims,
        malformed_cited_dois=_malformed_cited_dois(bib_entries, citation_keys),
    )


def extract_pandoc_citation_keys(text: str) -> tuple[str, ...]:
    """Extract Pandoc citation keys from bracket citation clusters."""

    stripped = _strip_code(text)
    keys: list[str] = []
    for cluster in _CITATION_CLUSTER_RE.findall(stripped):
        keys.extend(
            key
            for key in _CITATION_KEY_RE.findall(cluster)
            if not key.startswith(_CROSSREF_PREFIXES)
        )
    return tuple(dict.fromkeys(keys))


def parse_bibtex_entries(text: str) -> dict[str, dict[str, str]]:
    """Parse simple BibTeX entries into lowercase field dictionaries."""

    entries: dict[str, dict[str, str]] = {}
    for match in _ENTRY_RE.finditer(text):
        key = match.group("key").strip()
        body = match.group("body")
        fields: dict[str, str] = {"entry_type": match.group("kind").lower()}
        for field_match in _FIELD_RE.finditer(body):
            fields[field_match.group("field").lower()] = _collapse_whitespace(
                field_match.group("value")
            )
        entries[key] = fields
    return entries


def source_audit_markdown(audit: SourceAudit) -> str:
    """Render source audit results as Markdown."""

    lines = [
        "# BeeStack Source Audit",
        "",
        f"- Passed: `{audit.passed}`",
        f"- Citation keys used: `{len(audit.citation_keys)}`",
        f"- Bibliography keys: `{len(audit.bibliography_keys)}`",
        f"- Registry DOIs represented: `{len(audit.registry_dois_represented)}`",
        "",
        "## Missing Citation Keys",
        "",
        *_list_or_none(audit.missing_citation_keys),
        "",
        "## DOI Mismatches",
        "",
        *_list_or_none(audit.doi_mismatches),
        "",
        "## Missing Required Bibliography Fields",
        "",
        *_list_or_none(audit.missing_required_bib_fields),
        "",
        "## Registry DOIs Missing From Bibliography",
        "",
        *_list_or_none(audit.registry_dois_missing),
        "",
        "## Figure Registry Citation Keys Missing From Bibliography",
        "",
        *_list_or_none(audit.figure_registry_citation_keys_missing),
        "",
        "## Figure Registry DOIs Missing From Bibliography",
        "",
        *_list_or_none(audit.figure_registry_source_dois_missing),
        "",
        "## Unconservative Digital-Twin Claims",
        "",
        *_list_or_none(audit.unconservative_digital_twin_claims),
        "",
    ]
    return "\n".join(lines)


def _strip_code(text: str) -> str:
    return _INLINE_CODE_RE.sub("", _FENCED_CODE_RE.sub("", text))


def _doi_mismatches(
    entries: dict[str, dict[str, str]], expected_dois: Mapping[str, str]
) -> tuple[str, ...]:
    mismatches: list[str] = []
    for key, expected in expected_dois.items():
        entry = entries.get(key)
        if entry is None:
            mismatches.append(f"{key}: expected {expected}, found missing entry")
            continue
        found = entry.get("doi", "")
        if _normalize_doi(found) != _normalize_doi(expected):
            mismatches.append(f"{key}: expected {expected}, found {found or 'missing DOI'}")
    return tuple(mismatches)


_DOI_SHAPE_RE = re.compile(r"^10\.\d{4,9}/\S+$")


def _malformed_cited_dois(
    entries: dict[str, dict[str, str]], citation_keys: tuple[str, ...]
) -> tuple[str, ...]:
    """Flag every CITED entry whose ``doi`` field is present but malformed.

    Broadens DOI validation beyond the curated allowlist (the prior gate only
    shape-checked ``EXPECTED_BIB_DOIS``): any cited reference carrying a DOI that
    is not a well-formed ``10.NNNN/suffix`` string is surfaced as a release
    blocker. Resolution against a DOI registry is an online concern handled by
    the periodic Crossref audit, not this offline gate.
    """

    cited = set(citation_keys)
    malformed: list[str] = []
    for key in sorted(cited):
        entry = entries.get(key)
        if entry is None:
            continue
        doi = (entry.get("doi") or "").strip()
        if doi and not _DOI_SHAPE_RE.match(doi):
            malformed.append(f"{key}: malformed DOI {doi!r}")
    return tuple(malformed)


def _missing_required_fields(
    entries: dict[str, dict[str, str]], expected_dois: Mapping[str, str]
) -> tuple[str, ...]:
    missing: list[str] = []
    for key in expected_dois:
        entry = entries.get(key)
        if entry is None:
            missing.append(f"{key}: missing entry")
            continue
        for field in ("doi", "url"):
            if not entry.get(field):
                missing.append(f"{key}: missing {field}")
    return tuple(missing)


def _registry_doi_coverage(
    entries: dict[str, dict[str, str]],
    registry_dois: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    bib_dois = {_normalize_doi(fields.get("doi", "")) for fields in entries.values()}
    represented: list[str] = []
    missing: list[str] = []
    for doi in sorted({_normalize_doi(value) for value in registry_dois if value}):
        if doi in bib_dois:
            represented.append(doi)
        else:
            missing.append(doi)
    return tuple(represented), tuple(missing)


def _default_registry_dois() -> tuple[str, ...]:
    dois: list[str] = []
    for dataset in (*empirical_brain_datasets(), *empirical_anatomy_datasets()):
        if dataset.doi:
            dois.append(dataset.doi)
    return tuple(dois)


def _default_figure_registry_citation_keys() -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                key
                for narrative in all_figure_narratives()
                for key in (*narrative.citation_keys, *narrative.design_citation_keys)
            }
        )
    )


def _default_figure_registry_source_dois() -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                doi
                for narrative in all_figure_narratives()
                for doi in (*narrative.source_dois, *narrative.design_source_dois)
            }
        )
    )


def _unconservative_digital_twin_claims(
    project_root: Path,
    manuscript_text_by_path: dict[Path, str],
) -> tuple[str, ...]:
    claims: list[str] = []
    for path, text in manuscript_text_by_path.items():
        relative = path.resolve().relative_to(project_root).as_posix()
        for line in text.splitlines():
            clean = line.strip()
            lowered = _claim_scan_text(clean).lower()
            if "digital" not in lowered or "twin" not in lowered:
                continue
            if not any(
                re.search(rf"\b{re.escape(word)}\b", lowered) for word in _UNSAFE_TWIN_WORDS
            ):
                continue
            if any(
                re.search(rf"\b{re.escape(word)}\b", lowered) for word in _CONSERVATIVE_TWIN_WORDS
            ):
                continue
            claims.append(f"{relative}: {clean}")
    return tuple(claims)


def _claim_scan_text(text: str) -> str:
    text = _INLINE_CODE_RE.sub("", text)
    text = _CITATION_CLUSTER_RE.sub("", text)
    text = _TOKEN_RE.sub("", text)
    return text


def _normalize_doi(value: str) -> str:
    normalized = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
    return normalized.rstrip(".")


def _collapse_whitespace(value: str) -> str:
    return " ".join(value.replace("\n", " ").split())


def _list_or_none(values: tuple[str, ...]) -> list[str]:
    return [f"- `{value}`" for value in values] if values else ["- None detected."]
