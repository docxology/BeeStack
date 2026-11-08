"""Folder-guide generation must not mutate or populate packaging work trees."""

from __future__ import annotations

from beestack.documentation_signpost import write_signposts


def test_signposting_preserves_and_excludes_build_and_distribution_trees(tmp_path):
    source = tmp_path / "src/example"
    build = tmp_path / "build/lib/example"
    dist = tmp_path / "dist"
    for directory in (source, build, dist):
        directory.mkdir(parents=True)
    upstream = build / "README.md"
    upstream.write_text("Original package content\n")
    payload = dist / "artifact.bin"
    payload.write_bytes(b"original distribution bytes")
    result = write_signposts(tmp_path, overwrite=True)
    assert upstream.read_text() == "Original package content\n"
    assert payload.read_bytes() == b"original distribution bytes"
    assert not list((tmp_path / "build").rglob("AGENTS.md"))
    assert not (dist / "README.md").exists()
    assert not (dist / "AGENTS.md").exists()
    assert all(path.split("/")[0] not in {"build", "dist"} for path in result.readme_written)
    assert (source / "README.md").is_file() and (source / "AGENTS.md").is_file()
