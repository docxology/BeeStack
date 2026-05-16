"""Bee visual-signature checks for rendered BeeBody animations."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True)
class BeeRenderSignature:
    """Image and MJCF evidence that a render reads as a honeybee."""

    locomotion_mode: str
    frame_count: int
    image_shape: tuple[int, int, int]
    motion_pixels: int
    mean_adjacent_motion_pixels: float
    amber_fraction: float
    membrane_fraction: float
    dark_fraction: float
    debug_aid_fraction: float
    mjcf_features_present: tuple[str, ...]
    mjcf_features_missing: tuple[str, ...]
    silhouette_features_present: tuple[str, ...]
    silhouette_features_missing: tuple[str, ...]
    silhouette_score: float
    score: float
    locomotion_score: float

    @property
    def bee_like(self) -> bool:
        return (
            self.score >= 0.78
            and self.locomotion_score >= 1.0
            and self.silhouette_score >= 0.86
            and not self.mjcf_features_missing
            and not self.silhouette_features_missing
            and self.debug_aid_fraction < 0.003
        )

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["bee_like"] = self.bee_like
        return payload


_BEE_FEATURE_PATHS = {
    "apis model name": ".",
    "four-wing hindwing left": ".//geom[@name='apis_hindwing_left_membrane']",
    "four-wing hindwing right": ".//geom[@name='apis_hindwing_right_membrane']",
    "left pollen corbicula": ".//geom[@name='apis_corbicula_left']",
    "right pollen corbicula": ".//geom[@name='apis_corbicula_right']",
    "worker stinger": ".//geom[@name='apis_stinger']",
    "abdominal bee banding": ".//geom[@name='apis_abdomen_band_3']",
    "dorsal abdominal bee banding": ".//geom[@name='apis_abdomen_band_dorsal_3']",
    "thorax fuzz": ".//geom[@name='apis_thorax_fuzz_dorsal_0']",
    "dark compound eyes": ".//material[@name='apis_eye']",
    "enlarged left compound eye": ".//geom[@name='apis_compound_eye_left']",
    "enlarged right compound eye": ".//geom[@name='apis_compound_eye_right']",
    "left antenna": ".//geom[@name='apis_antenna_left']",
    "right antenna": ".//geom[@name='apis_antenna_right']",
}

_BEE_SILHOUETTE_PATHS = {
    "fuller amber abdomen": ".//geom[@name='apis_abdomen_fuller_3']",
    "strong black tergite band": ".//geom[@name='apis_abdomen_band_dorsal_3']",
    "four-wing left hindwing": ".//geom[@name='apis_hindwing_left_membrane']",
    "four-wing right hindwing": ".//geom[@name='apis_hindwing_right_membrane']",
    "left hamuli coupling": ".//geom[@name='apis_hamuli_left']",
    "right hamuli coupling": ".//geom[@name='apis_hamuli_right']",
    "large left compound eye": ".//geom[@name='apis_compound_eye_left']",
    "large right compound eye": ".//geom[@name='apis_compound_eye_right']",
    "left antenna visibility": ".//geom[@name='apis_antenna_left']",
    "right antenna visibility": ".//geom[@name='apis_antenna_right']",
    "proboscis visibility": ".//geom[@name='apis_proboscis']",
    "constricted bee waist": ".//geom[@name='apis_waist_petiole']",
}


def analyze_bee_render_signature(
    frames: list[np.ndarray],
    mjcf_xml: str,
    min_motion_pixels: int = 32,
    locomotion_mode: str = "walk",
) -> BeeRenderSignature:
    """Score actual rendered frames plus MJCF features for bee-like cues."""

    if not frames:
        raise ValueError("frames must not be empty")
    if min_motion_pixels <= 0:
        raise ValueError("min_motion_pixels must be positive")
    arrays = [np.asarray(frame) for frame in frames]
    shape = arrays[0].shape
    if len(shape) != 3 or shape[2] < 3:
        raise ValueError("frames must be RGB/RGBA arrays")
    if any(array.shape != shape for array in arrays):
        raise ValueError("frames must have consistent shape")

    rgb = np.concatenate([array[..., :3].reshape(-1, 3).astype(float) for array in arrays], axis=0)
    red, green, blue = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    amber = (red > 105) & (green > 45) & (green < 205) & (blue < 130) & (red >= green * 0.85)
    membrane = (
        (blue > 130) & (green > 110) & (red > 70) & ((blue - red) > 5) & ((green - red) > -25)
    )
    dark = (red < 70) & (green < 60) & (blue < 55)
    debug_aid = (red < 60) & (green > 160) & (blue > 150)

    motion_pixels = (
        int(np.count_nonzero(arrays[-1][..., :3] != arrays[0][..., :3])) if len(arrays) > 1 else 0
    )
    adjacent_motion = (
        [
            int(np.count_nonzero(arrays[idx + 1][..., :3] != arrays[idx][..., :3]))
            for idx in range(len(arrays) - 1)
        ]
        if len(arrays) > 1
        else [0]
    )
    mean_adjacent_motion = float(np.mean(adjacent_motion))
    present, missing = mjcf_bee_features(mjcf_xml)
    silhouette_present, silhouette_missing = mjcf_bee_silhouette_features(mjcf_xml)
    feature_score = len(present) / len(_BEE_FEATURE_PATHS)
    debug_clear_score = max(0.0, 1.0 - min(1.0, float(np.mean(debug_aid)) / 0.003))
    silhouette_score = (
        0.86 * (len(silhouette_present) / len(_BEE_SILHOUETTE_PATHS)) + 0.14 * debug_clear_score
    )
    locomotion_score = min(1.0, mean_adjacent_motion / min_motion_pixels)
    score = (
        0.30 * feature_score
        + 0.12 * silhouette_score
        + 0.12 * min(1.0, motion_pixels / min_motion_pixels)
        + 0.08 * locomotion_score
        + 0.18 * min(1.0, float(np.mean(amber)) / 0.010)
        + 0.12 * min(1.0, float(np.mean(membrane)) / 0.020)
        + 0.08 * min(1.0, float(np.mean(dark)) / 0.080)
    )
    return BeeRenderSignature(
        locomotion_mode=locomotion_mode,
        frame_count=len(frames),
        image_shape=(int(shape[0]), int(shape[1]), int(shape[2])),
        motion_pixels=motion_pixels,
        mean_adjacent_motion_pixels=mean_adjacent_motion,
        amber_fraction=float(np.mean(amber)),
        membrane_fraction=float(np.mean(membrane)),
        dark_fraction=float(np.mean(dark)),
        debug_aid_fraction=float(np.mean(debug_aid)),
        mjcf_features_present=present,
        mjcf_features_missing=missing,
        silhouette_features_present=silhouette_present,
        silhouette_features_missing=silhouette_missing,
        silhouette_score=float(silhouette_score),
        score=float(score),
        locomotion_score=float(locomotion_score),
    )


def mjcf_bee_features(mjcf_xml: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return present and missing bee-specific MJCF features from XML text."""

    return _mjcf_features(mjcf_xml, _BEE_FEATURE_PATHS)


def mjcf_bee_silhouette_features(mjcf_xml: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return present and missing MJCF cues for bee-vs-fly silhouette."""

    return _mjcf_features(mjcf_xml, _BEE_SILHOUETTE_PATHS)


def _mjcf_features(
    mjcf_xml: str, feature_paths: dict[str, str]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    root = ET.fromstring(mjcf_xml)
    present: list[str] = []
    missing: list[str] = []
    for label, path in feature_paths.items():
        if label == "apis model name":
            ok = root.get("model") == "apis_mellifera_worker"
        else:
            ok = root.find(path) is not None
        if ok:
            present.append(label)
        else:
            missing.append(label)
    return tuple(present), tuple(missing)


def bee_render_report_markdown(signature: BeeRenderSignature, gif_path: str, xml_path: str) -> str:
    """Create a concise Markdown report for human visual QA."""

    verdict = "PASS" if signature.bee_like else "FAIL"
    present = "\n".join(f"- {feature}" for feature in signature.mjcf_features_present)
    missing = "\n".join(f"- {feature}" for feature in signature.mjcf_features_missing) or "- none"
    silhouette_present = "\n".join(
        f"- {feature}" for feature in signature.silhouette_features_present
    )
    silhouette_missing = (
        "\n".join(f"- {feature}" for feature in signature.silhouette_features_missing) or "- none"
    )
    return "\n".join(
        [
            "# BeeBody Visual Verification",
            "",
            f"- Verdict: **{verdict}**",
            f"- Locomotion mode: `{signature.locomotion_mode}`",
            f"- GIF: `{gif_path}`",
            f"- MJCF: `{xml_path}`",
            f"- Score: `{signature.score:.3f}`",
            f"- Bee silhouette score: `{signature.silhouette_score:.3f}`",
            f"- Locomotion score: `{signature.locomotion_score:.3f}`",
            f"- Frames: `{signature.frame_count}`",
            f"- Motion pixels: `{signature.motion_pixels}`",
            f"- Mean adjacent motion pixels: `{signature.mean_adjacent_motion_pixels:.1f}`",
            f"- Amber body fraction: `{signature.amber_fraction:.4f}`",
            f"- Translucent wing/membrane fraction: `{signature.membrane_fraction:.4f}`",
            f"- Dark stripe/eye fraction: `{signature.dark_fraction:.4f}`",
            f"- Debug-aid color fraction: `{signature.debug_aid_fraction:.6f}`",
            "",
            "## Present Bee Cues",
            "",
            present,
            "",
            "## Missing Bee Cues",
            "",
            missing,
            "",
            "## Bee Silhouette Cues",
            "",
            silhouette_present,
            "",
            "## Missing Bee Silhouette Cues",
            "",
            silhouette_missing,
            "",
        ]
    )
