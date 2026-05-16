"""Bee-specific MJCF body-plan generation for FlyBody."""

from __future__ import annotations

import json
import shutil
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

from ..config import BeeStackConfig
from .morphology import bee_body_calibration_summary


class BeeBodyPlanError(RuntimeError):
    """Raised when a BeeBody MJCF plan cannot be created."""


@dataclass(frozen=True)
class BeeBodyPlanArtifact:
    """Generated BeeBody MJCF artifact metadata."""

    xml_path: str
    source_xml_path: str
    asset_dir: str
    manifest_path: str
    patch_count: int
    patches: tuple[str, ...]
    calibration_summary: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def locate_flybody_body_plan(fork_path: Path | None = None) -> Path:
    """Locate a FlyBody MJCF body plan, preferring a BeeStack fork target."""

    candidates: list[Path] = []
    if fork_path is not None:
        candidates.extend(
            [
                fork_path / "flybody" / "bee" / "assets" / "apis_mellifera_worker.xml",
                fork_path / "flybody" / "fruitfly" / "assets" / "fruitfly.xml",
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    try:
        fruitfly = import_module("flybody.fruitfly.fruitfly")
    except Exception as exc:  # pragma: no cover - depends on optional FlyBody install
        raise BeeBodyPlanError(
            "FlyBody is not importable; install the flybody extra first"
        ) from exc
    xml_path = Path(getattr(fruitfly, "_XML_PATH", ""))
    if not xml_path.exists():
        raise BeeBodyPlanError("FlyBody import succeeded, but fruitfly.xml was not found")
    return xml_path


def write_modified_bee_body_plan(
    cfg: BeeStackConfig,
    output_dir: Path,
    fork_path: Path | None = None,
) -> BeeBodyPlanArtifact:
    """Write a modified FlyBody MJCF asset set for an *Apis mellifera* worker.

    The output remains FlyBody-compatible: it keeps the upstream fruitfly mesh
    topology and task-facing joint names while changing the rendered body plan
    to expose honeybee-specific visual and biophysical adaptations. This lets
    FlyBody's own task classes load the model through ``walker_xml_path``.
    """

    source_xml = locate_flybody_body_plan(fork_path)
    source_assets = source_xml.parent
    asset_dir = output_dir / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    for asset in source_assets.iterdir():
        if asset.suffix.lower() in {".obj", ".xml", ".stl"}:
            shutil.copy2(asset, asset_dir / asset.name)

    tree = ET.parse(source_xml)
    root = tree.getroot()
    patches: list[str] = []
    _set(root, "model", cfg.body.species, patches, "model renamed to Apis worker target")
    asset_root = _required(root, "asset")
    _ensure_material(
        asset_root,
        "apis_gold",
        "0.87 0.58 0.12 1",
        patches,
        "bee mesosoma/metasoma amber material",
    )
    _ensure_material(
        asset_root,
        "apis_membrane",
        "0.73 0.90 1.0 0.48",
        patches,
        "translucent forewing/hindwing material",
    )
    _ensure_material(
        asset_root,
        "apis_pollen",
        "1.0 0.78 0.16 1",
        patches,
        "corbicula pollen-basket material",
    )
    _ensure_material(
        asset_root,
        "apis_dark_stripe",
        "0.045 0.025 0.010 1",
        patches,
        "dark abdominal stripe material",
    )
    _ensure_material(
        asset_root,
        "apis_fuzz",
        "0.96 0.72 0.34 1",
        patches,
        "golden thorax fuzz material",
    )
    _ensure_material(
        asset_root,
        "apis_eye",
        "0.025 0.018 0.012 1",
        patches,
        "dark compound-eye material",
    )
    _ensure_material(
        asset_root,
        "apis_mouthpart",
        "0.055 0.030 0.012 1",
        patches,
        "dark mandible and proboscis material",
    )
    _ensure_mesh(
        asset_root,
        "apis_hindwing_left_membrane",
        "wing_left_membrane.obj",
        "0.072 0.072 0.072",
        patches,
    )
    _ensure_mesh(
        asset_root,
        "apis_hindwing_right_membrane",
        "wing_right_membrane.obj",
        "0.072 0.072 0.072",
        patches,
    )

    for material_name, rgba in {
        "body": "0.63 0.36 0.12 1",
        "brown": "0.18 0.09 0.03 1",
        "membrane": "0.73 0.90 1.0 0.42",
        "red": "0.08 0.04 0.02 1",
        "lower": "0.045 0.025 0.010 1",
    }.items():
        material = asset_root.find(f"material[@name='{material_name}']")
        if material is not None:
            _set(
                material,
                "rgba",
                rgba,
                patches,
                f"{material_name} material recolored for honeybee body",
            )

    thorax = _required(root, ".//body[@name='thorax']")
    thorax_geom = thorax.find("geom[@name='thorax']")
    if thorax_geom is not None:
        # Keep this close to the FlyBody numerical scale while recording the
        # honeybee worker mass target in the generated manifest.
        _set(thorax_geom, "material", "apis_gold", patches, "thorax material set to Apis amber")
        _set(
            thorax_geom,
            "mass",
            f"{cfg.body.body_mass_mg / 250_000:.6g}",
            patches,
            "thorax mass normalized toward worker bee body mass",
        )
    _ensure_thorax_fuzz(thorax, patches)
    _ensure_compound_eye_material(root, patches)
    _ensure_head_bee_cues(root, patches)
    _ensure_bee_waist(root, patches)
    _ensure_camera(
        thorax,
        "bee_hero",
        "trackcom",
        "0.38 0.54 0.26",
        "-0.45 0.70 0 0.20 0.13 0.97",
        patches,
    )

    _ensure_hindwing(
        _required(root, ".//body[@name='wing_left']"),
        "left",
        "-0.082 0.026 -0.070",
        "-0.915 0 -0.403 0",
        patches,
    )
    _ensure_hindwing(
        _required(root, ".//body[@name='wing_right']"),
        "right",
        "0.082 -0.026 0.070",
        "-0.403 0 0.915 0",
        patches,
    )
    _ensure_corbicula(
        _required(root, ".//body[@name='tibia_T3_left']"), "left", "0.006 -0.045 0.000", patches
    )
    _ensure_corbicula(
        _required(root, ".//body[@name='tibia_T3_right']"), "right", "-0.006 0.045 0.000", patches
    )
    _ensure_stinger(_required(root, ".//body[@name='abdomen_7']"), patches)
    _ensure_abdominal_banding(root, patches)
    _ensure_hamuli_coupling_cues(root, patches)

    output_xml = asset_dir / "apis_mellifera_worker.xml"
    tree.write(output_xml, encoding="utf-8", xml_declaration=True)
    manifest_path = output_dir / "bee_body_plan_manifest.json"
    artifact = BeeBodyPlanArtifact(
        xml_path=str(output_xml),
        source_xml_path=str(source_xml),
        asset_dir=str(asset_dir),
        manifest_path=str(manifest_path),
        patch_count=len(patches),
        patches=tuple(patches),
        calibration_summary=bee_body_calibration_summary(cfg).as_dict(),
    )
    manifest_path.write_text(
        json.dumps(artifact.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return artifact


def validate_bee_body_plan_xml(xml_path: Path) -> tuple[str, ...]:
    """Validate that a generated MJCF file carries required BeeBody patches."""

    if not xml_path.exists():
        raise BeeBodyPlanError(f"BeeBody MJCF not found: {xml_path}")
    root = ET.parse(xml_path).getroot()
    required = (
        ".//geom[@name='apis_hindwing_left_membrane']",
        ".//geom[@name='apis_hindwing_right_membrane']",
        ".//geom[@name='apis_hamuli_left']",
        ".//geom[@name='apis_hamuli_right']",
        ".//geom[@name='apis_corbicula_left']",
        ".//geom[@name='apis_corbicula_right']",
        ".//geom[@name='apis_stinger']",
        ".//geom[@name='apis_compound_eye_left']",
        ".//geom[@name='apis_compound_eye_right']",
        ".//geom[@name='apis_antenna_left']",
        ".//geom[@name='apis_antenna_right']",
        ".//geom[@name='apis_mandible_left']",
        ".//geom[@name='apis_mandible_right']",
        ".//geom[@name='apis_proboscis']",
        ".//geom[@name='apis_waist_petiole']",
        ".//geom[@name='apis_abdomen_fuller_3']",
        ".//geom[@name='apis_abdomen_band_3']",
        ".//geom[@name='apis_abdomen_band_dorsal_3']",
        ".//geom[@name='apis_thorax_fuzz_dorsal_0']",
        ".//geom[@name='apis_thorax_fuzz_dorsal_5']",
        ".//camera[@name='bee_hero']",
    )
    missing = tuple(path for path in required if root.find(path) is None)
    if missing:
        raise BeeBodyPlanError(f"BeeBody MJCF missing required patches: {missing}")
    if root.get("model") != "apis_mellifera_worker":
        raise BeeBodyPlanError("BeeBody MJCF model must be apis_mellifera_worker")
    return required


def _required(root: ET.Element, path: str) -> ET.Element:
    found = root.find(path)
    if found is None:
        raise BeeBodyPlanError(f"required MJCF element not found: {path}")
    return found


def _set(element: ET.Element, key: str, value: str, patches: list[str], note: str) -> None:
    if element.get(key) != value:
        element.set(key, value)
        patches.append(note)


def _ensure_material(
    asset_root: ET.Element, name: str, rgba: str, patches: list[str], note: str
) -> None:
    material = asset_root.find(f"material[@name='{name}']")
    if material is None:
        ET.SubElement(asset_root, "material", {"name": name, "shininess": "0.7", "rgba": rgba})
        patches.append(note)
    else:
        _set(material, "rgba", rgba, patches, note)


def _ensure_mesh(
    asset_root: ET.Element, name: str, file_name: str, scale: str, patches: list[str]
) -> None:
    mesh = asset_root.find(f"mesh[@name='{name}']")
    if mesh is None:
        ET.SubElement(asset_root, "mesh", {"name": name, "file": file_name, "scale": scale})
        patches.append(f"{name} mesh added for four-wing honeybee plan")


def _ensure_camera(
    body: ET.Element,
    name: str,
    mode: str,
    pos: str,
    xyaxes: str,
    patches: list[str],
) -> None:
    if body.find(f"camera[@name='{name}']") is None:
        ET.SubElement(body, "camera", {"name": name, "mode": mode, "pos": pos, "xyaxes": xyaxes})
        patches.append("BeeBody camera added for real FlyBody rendering")


def _ensure_hindwing(body: ET.Element, side: str, pos: str, quat: str, patches: list[str]) -> None:
    name = f"apis_hindwing_{side}_membrane"
    if body.find(f"geom[@name='{name}']") is None:
        ET.SubElement(
            body,
            "geom",
            {
                "name": name,
                "material": "apis_membrane",
                "mass": "0",
                "pos": pos,
                "quat": quat,
                "mesh": f"apis_hindwing_{side}_membrane",
            },
        )
        patches.append(f"{side} hindwing geom added for coupled hamuli four-wing plan")


def _ensure_corbicula(body: ET.Element, side: str, pos: str, patches: list[str]) -> None:
    name = f"apis_corbicula_{side}"
    geom = body.find(f"geom[@name='{name}']")
    if geom is None:
        geom = ET.SubElement(
            body,
            "geom",
            {
                "name": name,
                "type": "ellipsoid",
                "material": "apis_pollen",
                "mass": "0",
                "size": "0.016 0.032 0.012",
                "pos": pos,
                "contype": "0",
                "conaffinity": "0",
                "group": "1",
            },
        )
        patches.append(f"{side} hind-leg corbicula added")
    else:
        _set(geom, "size", "0.016 0.032 0.012", patches, f"{side} corbicula enlarged")


def _ensure_compound_eye_material(root: ET.Element, patches: list[str]) -> None:
    for name in ("head_red", "head_black"):
        geom = root.find(f".//geom[@name='{name}']")
        if geom is not None:
            _set(
                geom,
                "material",
                "apis_eye",
                patches,
                f"{name} material set to dark compound-eye cue",
            )


def _ensure_head_bee_cues(root: ET.Element, patches: list[str]) -> None:
    head = root.find(".//body[@name='head']")
    if head is None:
        return
    cues = (
        (
            "apis_compound_eye_left",
            "ellipsoid",
            "apis_eye",
            {"size": "0.018 0.011 0.016", "pos": "-0.026 -0.019 -0.005"},
            "left enlarged compound-eye cue added",
        ),
        (
            "apis_compound_eye_right",
            "ellipsoid",
            "apis_eye",
            {"size": "0.018 0.011 0.016", "pos": "0.026 -0.019 -0.005"},
            "right enlarged compound-eye cue added",
        ),
        (
            "apis_antenna_left",
            "capsule",
            "apis_dark_stripe",
            {"fromto": "-0.010 -0.030 0.000 -0.054 -0.078 0.022", "size": "0.0018"},
            "left antenna added as honeybee head silhouette cue",
        ),
        (
            "apis_antenna_right",
            "capsule",
            "apis_dark_stripe",
            {"fromto": "0.010 -0.030 0.000 0.054 -0.078 0.022", "size": "0.0018"},
            "right antenna added as honeybee head silhouette cue",
        ),
        (
            "apis_mandible_left",
            "capsule",
            "apis_mouthpart",
            {"fromto": "-0.008 -0.034 -0.017 -0.028 -0.052 -0.024", "size": "0.0024"},
            "left mandible added",
        ),
        (
            "apis_mandible_right",
            "capsule",
            "apis_mouthpart",
            {"fromto": "0.008 -0.034 -0.017 0.028 -0.052 -0.024", "size": "0.0024"},
            "right mandible added",
        ),
        (
            "apis_proboscis",
            "capsule",
            "apis_mouthpart",
            {"fromto": "0.000 -0.038 -0.018 0.000 -0.073 -0.038", "size": "0.0022"},
            "proboscis added",
        ),
    )
    for name, geom_type, material, attrs, note in cues:
        geom = head.find(f"geom[@name='{name}']")
        if geom is None:
            ET.SubElement(
                head,
                "geom",
                {
                    "name": name,
                    "type": geom_type,
                    "material": material,
                    "mass": "0",
                    "contype": "0",
                    "conaffinity": "0",
                    "group": "1",
                    **attrs,
                },
            )
            patches.append(note)


def _ensure_bee_waist(root: ET.Element, patches: list[str]) -> None:
    abdomen = root.find(".//body[@name='abdomen']")
    if abdomen is None or abdomen.find("geom[@name='apis_waist_petiole']") is not None:
        return
    ET.SubElement(
        abdomen,
        "geom",
        {
            "name": "apis_waist_petiole",
            "type": "ellipsoid",
            "material": "apis_dark_stripe",
            "mass": "0",
            "size": "0.020 0.012 0.010",
            "pos": "0.000 -0.010 -0.016",
            "contype": "0",
            "conaffinity": "0",
            "group": "1",
        },
    )
    patches.append("constricted honeybee waist petiole cue added")


def _ensure_thorax_fuzz(body: ET.Element, patches: list[str]) -> None:
    fuzz_geoms = (
        ("dorsal_0", "-0.025 -0.030 -0.025 -0.028 -0.060 0.010"),
        ("dorsal_1", "-0.010 -0.033 -0.020 -0.010 -0.066 0.015"),
        ("dorsal_2", "0.006 -0.032 -0.020 0.010 -0.064 0.014"),
        ("dorsal_3", "0.024 -0.028 -0.022 0.030 -0.055 0.010"),
        ("dorsal_4", "-0.020 0.000 -0.018 -0.028 0.026 0.008"),
        ("dorsal_5", "0.020 0.000 -0.018 0.028 0.026 0.008"),
        ("left_0", "-0.026 -0.010 -0.020 -0.048 -0.015 0.000"),
        ("left_1", "-0.020 0.010 -0.018 -0.046 0.018 0.004"),
        ("left_2", "-0.020 -0.034 -0.012 -0.050 -0.050 0.010"),
        ("right_0", "0.026 -0.010 -0.020 0.048 -0.015 0.000"),
        ("right_1", "0.020 0.010 -0.018 0.046 0.018 0.004"),
        ("right_2", "0.020 -0.034 -0.012 0.050 -0.050 0.010"),
    )
    for suffix, fromto in fuzz_geoms:
        name = f"apis_thorax_fuzz_{suffix}"
        if body.find(f"geom[@name='{name}']") is None:
            ET.SubElement(
                body,
                "geom",
                {
                    "name": name,
                    "type": "capsule",
                    "material": "apis_fuzz",
                    "mass": "0",
                    "fromto": fromto,
                    "size": "0.0012",
                    "contype": "0",
                    "conaffinity": "0",
                    "group": "1",
                },
            )
            patches.append(f"{name} added as visible thorax fuzz cue")


def _ensure_abdominal_banding(root: ET.Element, patches: list[str]) -> None:
    abdomen_bodies = (
        ("abdomen", "0.000 0.005 -0.018", "0.032 0.006 0.011", "0.040 0.020 0.018"),
        ("abdomen_2", "0.000 0.014 -0.020", "0.039 0.006 0.012", "0.047 0.024 0.020"),
        ("abdomen_3", "0.000 0.017 -0.020", "0.044 0.006 0.013", "0.054 0.028 0.022"),
        ("abdomen_4", "0.000 0.014 -0.021", "0.044 0.006 0.013", "0.055 0.027 0.022"),
        ("abdomen_5", "0.000 0.010 -0.020", "0.040 0.006 0.012", "0.049 0.024 0.020"),
        ("abdomen_6", "0.000 0.009 -0.018", "0.035 0.005 0.011", "0.043 0.020 0.018"),
    )
    for index, (body_name, pos, band_size, fuller_size) in enumerate(abdomen_bodies, start=1):
        body = root.find(f".//body[@name='{body_name}']")
        if body is None:
            continue
        segment_geom = body.find(f"geom[@name='{body_name}']")
        if segment_geom is not None:
            _set(
                segment_geom,
                "material",
                "apis_gold",
                patches,
                f"{body_name} material set to amber abdominal tergite",
            )
        lower_geom = body.find(f"geom[@name='{body_name}_lower']")
        if lower_geom is not None:
            _set(
                lower_geom,
                "material",
                "apis_dark_stripe",
                patches,
                f"{body_name} lower material set to dark bee band",
            )
        fuller_name = f"apis_abdomen_fuller_{index}"
        fuller = body.find(f"geom[@name='{fuller_name}']")
        if fuller is None:
            ET.SubElement(
                body,
                "geom",
                {
                    "name": fuller_name,
                    "type": "ellipsoid",
                    "material": "apis_gold",
                    "mass": "0",
                    "size": fuller_size,
                    "pos": "0.000 0.006 -0.018",
                    "contype": "0",
                    "conaffinity": "0",
                    "group": "1",
                },
            )
            patches.append(f"{fuller_name} added for fuller worker-bee abdomen silhouette")
        band_name = f"apis_abdomen_band_{index}"
        band = body.find(f"geom[@name='{band_name}']")
        if band is None:
            band = ET.SubElement(
                body,
                "geom",
                {
                    "name": band_name,
                    "type": "ellipsoid",
                    "material": "apis_dark_stripe",
                    "mass": "0",
                    "size": band_size,
                    "pos": pos,
                    "contype": "0",
                    "conaffinity": "0",
                    "group": "1",
                },
            )
            patches.append(f"{band_name} added as honeybee abdominal band")
        else:
            _set(band, "size", band_size, patches, f"{band_name} strengthened")
        dorsal_name = f"apis_abdomen_band_dorsal_{index}"
        if body.find(f"geom[@name='{dorsal_name}']") is None:
            ET.SubElement(
                body,
                "geom",
                {
                    "name": dorsal_name,
                    "type": "capsule",
                    "material": "apis_dark_stripe",
                    "mass": "0",
                    "fromto": f"-{float(band_size.split()[0]) * 0.80:.3f} {pos.split()[1]} "
                    f"-0.030 {float(band_size.split()[0]) * 0.80:.3f} {pos.split()[1]} -0.030",
                    "size": "0.0038",
                    "contype": "0",
                    "conaffinity": "0",
                    "group": "1",
                },
            )
            patches.append(f"{dorsal_name} added as high-contrast dorsal tergite band")


def _ensure_hamuli_coupling_cues(root: ET.Element, patches: list[str]) -> None:
    cues = (
        ("wing_left", "left", "-0.073 0.016 -0.066 -0.108 0.032 -0.096"),
        ("wing_right", "right", "0.073 -0.016 0.066 0.108 -0.032 0.096"),
    )
    for body_name, side, fromto in cues:
        body = root.find(f".//body[@name='{body_name}']")
        if body is None or body.find(f"geom[@name='apis_hamuli_{side}']") is not None:
            continue
        ET.SubElement(
            body,
            "geom",
            {
                "name": f"apis_hamuli_{side}",
                "type": "capsule",
                "material": "apis_dark_stripe",
                "mass": "0",
                "fromto": fromto,
                "size": "0.0012",
                "contype": "0",
                "conaffinity": "0",
                "group": "1",
            },
        )
        patches.append(f"{side} hamuli coupling cue added between forewing and hindwing")


def _ensure_stinger(body: ET.Element, patches: list[str]) -> None:
    if body.find("geom[@name='apis_stinger']") is None:
        ET.SubElement(
            body,
            "geom",
            {
                "name": "apis_stinger",
                "type": "capsule",
                "material": "black",
                "mass": "0",
                "fromto": "0 0.014 -0.015 0 0.040 -0.030",
                "size": "0.002",
                "contype": "0",
                "conaffinity": "0",
                "group": "1",
            },
        )
        patches.append("stinger effector geom added to terminal abdomen")
