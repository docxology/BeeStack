from __future__ import annotations

import math
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from beestack.body import (
    BodyState,
    bee_body_calibration_summary,
    cost_of_transport,
    honeybee_calibration_targets,
    initial_body_state,
    morphology_summary,
    observation_from_state,
    step_body,
    walking_power_mw,
    wing_power_mw,
)
from beestack.brain import (
    AtlasDownloadRecord,
    BeeBrainActivitySummary,
    BeeBrainDataCompletenessPanel,
    BeeBrainEndToEndReport,
    BeeBrainSourceGap,
    BeeBrainSourceStatus,
    activity_summary_from_components,
    all_checks_passed,
    analyze_odor_panel,
    angular_distance_deg,
    antennal_vibration_from_movement,
    atlas_download_record_from_asset,
    atlas_download_records_from_dicts,
    atlas_inventories_from_directory,
    atlas_inventory_from_zip,
    bee_brain_data_completeness_panel,
    build_empirical_template_bank,
    circular_mean_deg,
    dataset_by_id,
    decode_waggle,
    empirical_alignment_score,
    empirical_anatomy_datasets,
    empirical_brain_datasets,
    empirical_brain_profile,
    empirical_odor_response_templates,
    glomerular_encode,
    heading_ring,
    honeybee_standard_brain_assets,
    kenyon_sparse_code,
    load_neuropil_abbreviations,
    negative_delta_f_over_f,
    neuropil_abbreviations_from_html,
    odor_panel_sparseness,
    parse_paoli_matlab_payload,
    parse_tabular_odor_response_rows,
    process_observation,
    response_templates_from_calcium_dataset,
    response_templates_from_odor_panel,
    summarize_anatomy,
    summarize_antennal_movement_rows,
    summarize_calcium_trials,
    summarize_waggle_follower_rows,
    template_alignment_matrix,
    validate_calcium_dataset,
    validate_odor_panel,
    waggle_decoding_diagnostics,
    waggle_kinematics_from_config,
    waggle_vibration_from_followers,
)
from beestack.config import BeeStackConfig, config_from_mapping
from beestack.contracts import Action, validate_observation, zero_observation


def test_morphology_summary_and_power_calibration() -> None:
    cfg = BeeStackConfig()
    summary = morphology_summary(cfg)
    assert summary["leg_dof"] == 24
    assert summary["wing_dof"] == 12
    assert summary["morphology_score"] >= 0.85
    calibration = bee_body_calibration_summary(cfg)
    assert calibration.morphology_score >= 0.85
    assert calibration.inertia_rescaling_score > 0
    assert calibration.contact_proxy_count >= 3
    targets = honeybee_calibration_targets(cfg)
    assert {target.name for target in targets} >= {"worker_body_mass", "forewing_hindwing_pairs"}
    assert all(target.as_dict()["value"] > 0 for target in targets)
    assert 40 <= wing_power_mw(80.0, 230.0) <= 80
    assert wing_power_mw(80.0, 230.0, load_fraction=0.3) > wing_power_mw(80.0, 230.0)
    assert walking_power_mw(80.0, 0.1) > walking_power_mw(80.0, 0.0)
    assert math.isinf(cost_of_transport(10.0, 80.0, 0.0))
    assert cost_of_transport(58.0, 80.0, 1.0) > 0
    with pytest.raises(ValueError, match="speed_m_s"):
        walking_power_mw(80.0, -0.1)
    with pytest.raises(ValueError, match="terrain_factor"):
        walking_power_mw(80.0, 0.1, terrain_factor=0.0)
    with pytest.raises(ValueError, match="power_mw"):
        cost_of_transport(-1.0, 80.0, 1.0)
    with pytest.raises(ValueError, match="mass_mg"):
        cost_of_transport(1.0, 0.0, 1.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mass_mg": 0, "stroke_hz": 230},
        {"mass_mg": 80, "stroke_hz": 0},
        {"mass_mg": 80, "stroke_hz": 230, "load_fraction": -1},
        {"mass_mg": 80, "stroke_hz": 230, "wing_area_loss_fraction": 1},
    ],
)
def test_wing_power_rejects_invalid_inputs(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        wing_power_mw(**kwargs)


def test_step_body_produces_valid_observation_and_consumes_energy() -> None:
    cfg = BeeStackConfig()
    state = BodyState(position_m=np.zeros(3), velocity_m_s=np.zeros(3), heading_deg=0.0)
    action = Action(legs=np.ones(cfg.body.leg_dof) * 0.2, wings=np.ones(cfg.body.wing_dof) * 0.8)
    next_state, obs, telemetry = step_body(state, action, cfg)
    validate_observation(obs, cfg)
    assert next_state.position_m[0] > state.position_m[0]
    assert next_state.energy_j < state.energy_j
    assert telemetry.speed_m_s > 0
    assert telemetry.wing_power_mw >= 58.0
    with pytest.raises(ValueError, match="dt_s"):
        step_body(state, action, cfg, dt_s=0)


def test_initial_body_state_is_seed_deterministic() -> None:
    a = initial_body_state(10)
    b = initial_body_state(10)
    c = initial_body_state(11)
    assert np.allclose(a.position_m, b.position_m)
    assert a.heading_deg == b.heading_deg
    assert not np.allclose(a.position_m, c.position_m)
    obs = observation_from_state(a, BeeStackConfig())
    assert obs.ocelli.shape == (3,)


def test_glomerular_encode_normalizes_and_resamples() -> None:
    cfg = BeeStackConfig()
    encoded = glomerular_encode(np.linspace(0, 10, 20), cfg)
    assert encoded.shape == (cfg.brain.glomeruli,)
    assert encoded.max() == pytest.approx(1.0)
    direct = glomerular_encode(np.ones(cfg.brain.glomeruli), cfg)
    assert direct.shape == (cfg.brain.glomeruli,)
    with pytest.raises(ValueError, match="vector"):
        glomerular_encode(np.zeros((2, 2)), cfg)


def test_kenyon_sparse_code_respects_sparsity_and_seed() -> None:
    cfg = config_from_mapping({"brain": {"kenyon_cells_per_hemisphere": 1000, "kc_sparsity": 0.02}})
    glom = np.ones(cfg.brain.glomeruli)
    code_a = kenyon_sparse_code(glom, cfg, seed=3)
    code_b = kenyon_sparse_code(glom, cfg, seed=3)
    assert code_a.total_cells == 2000
    assert code_a.active_fraction <= 0.02
    assert np.array_equal(code_a.active_indices, code_b.active_indices)
    assert np.all((code_a.activations >= 0) & (code_a.activations <= 1))
    with pytest.raises(ValueError, match="glomerular_activation"):
        kenyon_sparse_code(np.ones(2), cfg, seed=1)


def test_kenyon_sparse_code_is_odor_specific() -> None:
    """Different odors must drive different sparse KC sets (regression: the

    code formerly drew indices from the seed alone and was odor-invariant).
    """

    cfg = config_from_mapping({"brain": {"kenyon_cells_per_hemisphere": 4000, "kc_sparsity": 0.02}})
    rng = np.random.default_rng(11)
    odor_a = rng.random(cfg.brain.glomeruli)
    odor_b = rng.random(cfg.brain.glomeruli)
    code_a = kenyon_sparse_code(odor_a, cfg, seed=7)
    code_b = kenyon_sparse_code(odor_b, cfg, seed=7)
    code_a_again = kenyon_sparse_code(odor_a, cfg, seed=7)
    # Same odor + seed is reproducible.
    assert np.array_equal(code_a.active_indices, code_a_again.active_indices)
    # Different odors at the same seed select a materially different set.
    set_a = set(code_a.active_indices.tolist())
    set_b = set(code_b.active_indices.tolist())
    jaccard = len(set_a & set_b) / len(set_a | set_b)
    assert jaccard < 0.5
    assert code_a.active_fraction <= cfg.brain.kc_sparsity


def test_heading_ring_and_angle_helpers() -> None:
    cfg = BeeStackConfig()
    ring = heading_ring(350.0, 10.0, np.array([1.0, 0.0]), cfg)
    assert ring.shape == (cfg.brain.heading_bins,)
    assert ring.sum() == pytest.approx(1.0)
    assert angular_distance_deg(350, 10) == pytest.approx(20)
    assert circular_mean_deg([350, 10], [0.5, 0.5]) == pytest.approx(0.0, abs=1e-9)
    with pytest.raises(ValueError, match="optic_flow"):
        heading_ring(0, 0, np.ones(3), cfg)
    with pytest.raises(ValueError, match="same nonzero"):
        circular_mean_deg([], [])


def test_waggle_decode_and_observation_pipeline() -> None:
    cfg = BeeStackConfig()
    dance = decode_waggle(duration_s=1.2, angle_deg=35.0, sun_azimuth_deg=120.0, quality_score=0.8)
    assert dance.distance_km == pytest.approx(1.2)
    assert dance.azimuth_deg == pytest.approx(155.0)
    assert 0 < dance.confidence <= 1
    with pytest.raises(ValueError, match="duration"):
        decode_waggle(-1, 0, 0, 1)
    obs = zero_observation(cfg)
    vibrating = obs.__class__(
        **{
            **obs.__dict__,
            "antennal_vibration": np.array([0.6, 250.0]),
            "antennal_channels": np.ones(cfg.body.olfactory_channels),
        }
    )
    brain = process_observation(vibrating, cfg, seed=1)
    assert brain.decoded_dance is not None
    assert brain.kc_code.active_fraction <= 0.02
    assert "dryad-paoli-2024-al-calcium" in brain.empirical_dataset_ids
    assert set(brain.empirical_alignment) == {"1-octanol", "clove oil", "geraniol"}


def test_empirical_beebrain_dataset_registry_and_calcium_summaries() -> None:
    cfg = BeeStackConfig()
    datasets = empirical_brain_datasets()
    ids = {dataset.dataset_id for dataset in datasets}
    assert "dryad-paoli-2024-al-calcium" in ids
    assert "dryad-carcaud-2022-multisite-gcamp" in ids
    assert "dryad-andreu-2025-alarm-odorant-receptors" in ids
    assert "dryad-jernigan-2026-antennal-movement" in ids
    assert "dryad-nouvian-2017-biogenic-amines" in ids
    assert "figshare-hadjitofi-2024-waggle-following" in ids
    assert "virtual-honeybee-standard-brain" in ids
    waggle_dataset = dataset_by_id("figshare-hadjitofi-2024-waggle-following")
    assert waggle_dataset.license_note.startswith("CC BY 4.0")
    assert "waggle_decoding" in waggle_dataset.module_targets
    assert dataset_by_id("galizia-1999-glomerular-code").doi == "10.1038/8144"
    anatomy = empirical_anatomy_datasets()
    assert anatomy[0].dataset_id == "virtual-honeybee-standard-brain"
    assert {asset.asset_type for asset in honeybee_standard_brain_assets()} >= {
        "tiff_stack",
        "label_field",
        "vrml",
        "html_table",
    }
    assert dataset_by_id("kaneko-2016-kenyon-subtypes").module_targets == ("mushroom_body",)
    with pytest.raises(KeyError, match="unknown empirical"):
        dataset_by_id("missing")
    profile = empirical_brain_profile(cfg)
    assert profile.default_glomeruli == cfg.brain.glomeruli
    assert profile.calcium_protocol.acquisition_hz == 100.0
    custom_cfg = config_from_mapping(
        {
            "empirical": {
                "enabled_dataset_ids": ["dryad-paoli-2024-al-calcium"],
                "calcium_acquisition_hz": 50.0,
                "calcium_baseline_s": 0.5,
                "calcium_stimulus_s": [0.5, 1.0],
                "odor_templates": ["hexanal"],
                "template_excitation_width": 0.06,
            }
        }
    )
    custom_profile = empirical_brain_profile(custom_cfg)
    assert custom_profile.dataset_ids == ("dryad-paoli-2024-al-calcium",)
    assert custom_profile.calcium_protocol.baseline_frames == 25
    assert custom_profile.calcium_protocol.stimulus_frame_window == (25, 50)
    # Worked sign-convention example. `negative_delta_f_over_f` negates ΔF/F:
    #   excitation = fluorescence UP (1.0 -> 1.4) -> ΔF/F = +0.4 -> negated -0.4
    #   inhibition = fluorescence DOWN (1.0 -> 0.7) -> ΔF/F = -0.3 -> negated +0.3
    traces = np.ones((2, 240, cfg.brain.glomeruli), dtype=float)
    traces[:, 100:140, :5] = 1.4  # five excitatory glomeruli
    traces[:, 100:140, 5:8] = 0.7  # three inhibitory glomeruli
    normalized = negative_delta_f_over_f(traces, baseline_frames=5)
    assert normalized.shape == traces.shape
    assert normalized[:, 100:140, :5].mean() == pytest.approx(-0.4)
    assert normalized[:, 100:140, 5:8].mean() == pytest.approx(0.3)
    summary = summarize_calcium_trials(traces, profile.calcium_protocol)
    assert summary.mean_response.shape == (cfg.brain.glomeruli,)
    assert summary.excitatory_fraction > 0  # the increasing glomeruli
    assert summary.inhibitory_fraction > 0  # the decreasing glomeruli
    assert summary.excitatory_fraction + summary.inhibitory_fraction <= 1.0
    templates = empirical_odor_response_templates(cfg)
    assert templates["1-octanol"].shape == (cfg.brain.glomeruli,)
    assert set(empirical_odor_response_templates(custom_cfg)) == {"hexanal"}
    assert -1 <= empirical_alignment_score(templates["1-octanol"], templates["clove oil"]) <= 1
    with pytest.raises(KeyError, match="unknown empirical"):
        empirical_brain_profile(
            config_from_mapping(
                {
                    "empirical": {
                        "enabled_dataset_ids": ["not-registered"],
                        "calcium_source_dataset_id": "not-registered",
                    }
                }
            )
        )
    with pytest.raises(ValueError, match="odorants"):
        empirical_odor_response_templates(cfg, tuple())
    with pytest.raises(ValueError, match="matching"):
        empirical_alignment_score(np.ones(2), np.ones(3))
    with pytest.raises(ValueError, match="baseline_frames"):
        negative_delta_f_over_f(traces, baseline_frames=0)


def test_real_empirical_dataset_parsers_feed_beebrain_templates() -> None:
    cfg = config_from_mapping(
        {
            "brain": {"glomeruli": 12},
            "empirical": {"calcium_baseline_s": 0.2, "calcium_stimulus_s": [0.2, 0.5]},
        }
    )
    paoli_payload = {
        "db": {
            "bee": [
                np.stack(
                    [
                        np.ones((2, 3, 60)) * 1.0,
                        np.ones((2, 3, 60)) * 1.0,
                        np.ones((2, 3, 60)) * 1.0,
                        np.ones((2, 3, 60)) * 1.0,
                    ],
                    axis=0,
                )
            ],
            "fs": 100,
            "odors": ["octanol", "clove"],
            "glomeruli": ["T1-17", "T1-28", "T1-33", "T1-37"],
        }
    }
    paoli_payload["db"]["bee"][0][0, 0, :, 20:50] = 0.7
    calcium_dataset = parse_paoli_matlab_payload(paoli_payload)
    assert calcium_dataset.traces.shape == (1, 2, 3, 60, 4)
    templates = response_templates_from_calcium_dataset(calcium_dataset, cfg)
    assert set(templates) == {"octanol", "clove"}
    assert templates["octanol"].shape == (cfg.brain.glomeruli,)
    obs = zero_observation(cfg)
    brain = process_observation(obs, cfg, seed=2, odor_templates=templates)
    assert set(brain.empirical_alignment) == {"octanol", "clove"}

    rows = [
        {"odor": "alarm", "channel": "AmOR136", "response": 1.0},
        {"odor": "alarm", "channel": "AmOR11", "response": 0.2},
        {"odor": "hexanol", "channel": "AmOR136", "response": 0.1},
        {"odor": "hexanol", "channel": "AmOR11", "response": 0.9},
    ]
    panel = parse_tabular_odor_response_rows(
        "dryad-andreu-2025-alarm-odorant-receptors",
        rows,
        stimulus_key="odor",
        response_key="response",
        channel_key="channel",
        modality="odorant receptor panel",
        units="normalized current",
    )
    panel_templates = response_templates_from_odor_panel(panel, cfg)
    assert set(panel_templates) == {"alarm", "hexanol"}
    assert odor_panel_sparseness(panel)["alarm"] >= 0
    assert all_checks_passed(validate_odor_panel(panel))
    assert all_checks_passed(validate_calcium_dataset(calcium_dataset))
    stats = analyze_odor_panel(panel)
    assert stats.stimulus_count == 2
    assert stats.top_stimuli
    bank = build_empirical_template_bank((panel,), cfg)
    assert bank.templates["alarm"].shape == (cfg.brain.glomeruli,)
    assert "alarm" in template_alignment_matrix(bank)
    assert bank.as_dict()["template_count"] == 2
    with pytest.raises(ValueError, match="max_templates"):
        bank.limited(0)
    with pytest.raises(ValueError, match="at least one"):
        build_empirical_template_bank(tuple(), cfg)
    movement = summarize_antennal_movement_rows(
        [
            {
                "Bee": "B1",
                "Plume": "bounded",
                "Frame": "1",
                "Odor_detector": "On",
                "LeftTheta": "350",
                "RightTheta": "-8",
                "deriv1LeftTheta": "5",
                "deriv1RightTheta": "7",
            },
            {
                "Bee": "B1",
                "Plume": "unbounded",
                "Frame": "2",
                "Odor_detector": "Off",
                "LeftTheta": "10",
                "RightTheta": "12",
                "deriv1LeftTheta": "6",
                "deriv1RightTheta": "8",
            },
        ]
    )
    assert movement.row_count == 2
    assert movement.bee_count == 1
    assert movement.plume_count == 2
    assert movement.odor_on_fraction == pytest.approx(0.5)
    assert movement.mean_abs_left_theta_deg == pytest.approx(10.0)
    vibration = antennal_vibration_from_movement(movement)
    assert vibration.shape == (2,)
    assert vibration[0] == pytest.approx(0.26)
    assert vibration[1] == pytest.approx(250.0)
    activity_summary = activity_summary_from_components(
        (panel,),
        (stats,),
        bank,
        antennal_summaries=(movement,),
        calcium_summaries=(
            summarize_calcium_trials(calcium_dataset.traces, calcium_dataset.protocol(cfg)),
        ),
        quality_checks=tuple(check for check in validate_odor_panel(panel))
        + validate_calcium_dataset(calcium_dataset),
    )
    assert activity_summary.panel_count == 1
    assert activity_summary.calcium_dataset_count == 1
    assert activity_summary.antennal_active_sensing_drive["odor_on_fraction"] == pytest.approx(0.5)
    assert activity_summary.mean_odor_separability >= 0
    assert activity_summary.as_dict()["template_count"] == 2


def test_honeybee_standard_brain_anatomy_parsers(tmp_path: Path) -> None:
    html = """
    <table>
      <tr><th>Abbreviation</th><th>Name</th></tr>
      <tr><td>l-AL</td><td>left antennal lobe</td></tr>
      <tr><td>r-AL</td><td>right antennal lobe</td></tr>
      <tr><td>MB</td><td>mushroom body calyx</td></tr>
      <tr><td>PB</td><td>protocerebral bridge</td></tr>
      <tr><td>left Lobula</td><td>l-Lob</td></tr>
    </table>
    <ul><li>CB= Central Body</li><li>CB= Central Body duplicate</li></ul>
    """
    abbreviations = neuropil_abbreviations_from_html(html)
    assert {entry.region_class for entry in abbreviations} >= {
        "antennal_lobe",
        "mushroom_body",
        "central_complex",
    }
    html_path = tmp_path / "neuropil_abbreviations.html"
    html_path.write_text(html, encoding="utf-8")
    assert len(load_neuropil_abbreviations(html_path)) == len(abbreviations)
    assert load_neuropil_abbreviations(tmp_path / "missing.html") == ()
    image_bytes = BytesIO()
    Image.new("L", (4, 3), color=7).save(image_bytes, format="TIFF")
    vrml = b"""
    Shape {
      geometry IndexedFaceSet {
        coord Coordinate { point [0 0 0, 1 0 0, 0 1 0] }
        coordIndex [0, 1, 2, -1]
      }
    }
    """
    archive_path = tmp_path / "HBSLabels.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("labels/stack_0001.tif", image_bytes.getvalue())
        archive.writestr("atlas/neuropil.wrl", vrml)
    inventory = atlas_inventory_from_zip(archive_path, asset_id="fixture-atlas")
    auto_inventory = atlas_inventory_from_zip(archive_path)
    assert inventory.tiff_count == 1
    assert inventory.vrml_count == 1
    assert inventory.image_shape == (3, 4)
    assert inventory.vrml_vertex_count == 3
    assert inventory.vrml_face_count == 1
    assert inventory.vrml_bounds_min == (0.0, 0.0, 0.0)
    assert inventory.vrml_bounds_max == (1.0, 1.0, 0.0)
    assert inventory.vrml_centroid == pytest.approx((1 / 3, 1 / 3, 0.0))
    assert auto_inventory.asset_id == "hsb-hbslabels"
    assert atlas_inventories_from_directory(tmp_path)[0].file_count == 2
    record = AtlasDownloadRecord(
        dataset_id="virtual-honeybee-standard-brain",
        asset_id="fixture-atlas",
        url="https://example.org/HBSLabels.zip",
        local_path=str(archive_path),
        size_bytes=archive_path.stat().st_size,
        downloaded=True,
        skipped_existing=True,
    )
    asset_record = atlas_download_record_from_asset(
        "virtual-honeybee-standard-brain",
        honeybee_standard_brain_assets()[0],
        archive_path,
        skipped_existing=True,
        sha256="fixture",
    )
    assert asset_record.downloaded
    assert atlas_download_records_from_dicts((asset_record.as_dict(),))[0].sha256 == "fixture"
    assert record.as_dict()["downloaded"] is True
    assert inventory.as_dict()["vrml_count"] == 1
    assert abbreviations[0].as_dict()["abbreviation"]
    summary = summarize_anatomy((record,), (inventory,), abbreviations)
    assert summary.downloaded_asset_count == 1
    assert summary.bilateral_pair_count == 1
    assert summary.major_regions["antennal_lobe"] == 2
    assert summary.major_regions["optic_lobe"] == 1
    activity = BeeBrainActivitySummary(
        panel_count=0,
        calcium_dataset_count=0,
        antennal_movement_summary_count=0,
        template_count=0,
        all_quality_checks_passed=True,
        mean_odor_separability=0.0,
        calcium_mean_latency_s=0.0,
        calcium_inhibitory_fraction=0.0,
        calcium_excitatory_fraction=0.0,
        aftersmell_response_mean=0.0,
        region_response_means={},
        antennal_active_sensing_drive={},
        neuromodulatory_defence_summary={},
    )
    report = BeeBrainEndToEndReport(
        anatomy=summary,
        activity=activity,
        dataset_ids=("fixture",),
        figure_paths=("figure.png",),
        archive_status=({"dataset_id": "fixture"},),
        anatomy_downloads=(record.as_dict(),),
        known_gaps=("none",),
    )
    assert report.as_dict()["anatomy"]["neuropil_count"] == len(abbreviations)
    with pytest.raises(ValueError, match="rows"):
        summarize_antennal_movement_rows([])
    with pytest.raises(ValueError, match="rows"):
        parse_tabular_odor_response_rows(
            "empty", [], "odor", "response", "channel", "modality", "units"
        )


def test_waggle_follower_dataset_parser_and_diagnostics() -> None:
    cfg = config_from_mapping({"waggle": {"follower_orientation_gain": 0.8}})
    features = [
        {
            "bee_id": "n1",
            "frame": "1",
            "angle_to_dancer_deg": "-90",
            "dancers_angle_to_gravity_deg": "30",
            "l_antenna_deg": "35",
            "r_antenna_deg": "-32",
            "antenna_midpoint_deg": "2",
            "s_s_deg": "67",
        },
        {
            "bee_id": "n1",
            "frame": "2",
            "angle_to_dancer_deg": "-80",
            "dancers_angle_to_gravity_deg": "32",
            "l_antenna_deg": "38",
            "r_antenna_deg": "-31",
            "antenna_midpoint_deg": "4",
            "s_s_deg": "69",
        },
        {
            "bee_id": "n2",
            "frame": "1",
            "angle_to_dancer_deg": "90",
            "dancers_angle_to_gravity_deg": "31",
            "l_antenna_deg": "30",
            "r_antenna_deg": "-37",
            "antenna_midpoint_deg": "-3",
            "s_s_deg": "67",
        },
    ]
    binned = [
        {"bin_idx_of_angle_to_dancer_deg": "-90", "midpt_mean_deg": "2"},
        {"bin_idx_of_angle_to_dancer_deg": "90", "midpt_mean_deg": "-3"},
    ]
    model_errors = [
        {
            "_source_file": "both_antennae-reduced_errors.csv",
            "bee_id": "n1",
            "mean_rad": "0.2",
        },
        {
            "_source_file": "no_antennae-reduced_errors.csv",
            "bee_id": "n1",
            "mean_rad": "0.8",
        },
        {
            "_source_file": "both_antennae-errors.csv",
            "bee_id": "n2",
            "vector_error_deg": "8",
        },
    ]
    parsed = summarize_waggle_follower_rows(
        features,
        binned_rows=binned,
        model_error_rows=model_errors,
        straightness_rows=({"bee_id": "n1", "straightness": "0.9"},),
    )
    assert parsed.dataset_id == "figshare-hadjitofi-2024-waggle-following"
    assert parsed.summary.track_count == 2
    assert parsed.summary.feature_row_count == 3
    assert parsed.summary.binned_row_count == 2
    assert parsed.summary.model_error_row_count == 3
    assert parsed.summary.decoding_improvement_fraction > 0
    assert 0 <= parsed.summary.confidence_score <= 1
    vibration = waggle_vibration_from_followers(parsed.summary)
    assert vibration.shape == (2,)
    assert vibration[1] >= 200.0
    diagnostics = waggle_decoding_diagnostics(
        cfg,
        empirical_confidence=parsed.summary.confidence_score,
        mean_orientation_error_deg=12.0,
        mean_follower_distance_m=0.11,
    )
    assert diagnostics.kinematics.waggle_run_frequency_hz == 13.0
    assert diagnostics.confidence_terms["combined_confidence"] > 0
    assert waggle_kinematics_from_config(cfg).follower_spacing_m == pytest.approx(0.11)
    completeness = bee_brain_data_completeness_panel(
        empirical_brain_datasets(),
        downloaded_dataset_ids=("figshare-hadjitofi-2024-waggle-following",),
        parseable_dataset_ids=("figshare-hadjitofi-2024-waggle-following",),
        parser_status_by_dataset={"figshare-hadjitofi-2024-waggle-following": "parsed"},
    )
    payload = completeness.as_dict()
    assert payload["dataset_count"] >= 10
    assert "waggle_decoding" in payload["module_target_counts"]
    assert completeness.source_verified_fraction == pytest.approx(1.0)
    assert not completeness.parseability_target_satisfied
    assert all(isinstance(gap, BeeBrainSourceGap) for gap in completeness.source_gaps)
    assert all(isinstance(status, BeeBrainSourceStatus) for status in completeness.source_statuses)
    panel = BeeBrainDataCompletenessPanel(
        dataset_count=1,
        downloaded_dataset_count=1,
        parseable_dataset_count=1,
        source_verified_dataset_count=1,
        source_verified_blocked_count=0,
        parseability_target=0.8,
        modality_counts={"csv": 1},
        module_target_counts={"waggle": 1},
        module_modality_matrix={"waggle": {"csv": 1}},
        source_gaps=(),
        source_statuses=(
            BeeBrainSourceStatus(
                "test",
                "https://example.com",
                "10.1/test",
                True,
                True,
                True,
                "parsed",
                "",
                "none",
            ),
        ),
    )
    assert panel.parseable_fraction == pytest.approx(1.0)
    with pytest.raises(ValueError, match="waggle follower feature rows"):
        summarize_waggle_follower_rows([])
