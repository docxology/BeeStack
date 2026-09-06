# Configuration

BeeStack is driven by `docs/manuscript/config.yaml`, loaded by the thin scripts and
validated by `src/beestack/config.py`.

## Sections

- `timing`: physics step, control rate, policy rate, and dance-event rate.
- `body`: honeybee morphology, sensory dimensions, wing model, terrain, and
  sensor noise.
- `brain`: antennal-lobe, mushroom-body, and central-complex scale parameters.
- `mind`: belief dimension, caste prior, policy horizon, and noise levels.
- `swarm`: agent count, represented colony size, pheromone grid, and dance
  recruitment fan-out.
- `niche`: comb grid, brood thermal band, wax threshold, ambient temperature,
  and foraging radius.
- `flybody`: FlyBody action dimension, local fork path, walk-imitation
  task options, rollout horizon, and rendered-frame motion validation.
- `empirical`: BeeBrain dataset IDs, calcium-imaging protocol metadata,
  atlas-glomerulus range, odor-template names, and template shape parameters.
- `visualization`: module animation frames/fps, BeeBody camera/render/body-plan
  settings, strict MuJoCo scene substeps, swarm collision bee count/speed/
  radius/altitude/contact requirement, and waggle-dance duration, angle, sun
  azimuth, quality, follower count, waggle amplitude, loop radius, and long
  waggle animation frame/fps settings.
- `waggle`: domain-level waggle kinematics and recruitment settings: waggle-run
  frequency, lateral amplitude, loop radius, follower spacing, follower
  orientation gain, antennal sampling gain, stop-signal sensitivity, and maximum
  orientation error plus strict orientation-error and confidence targets.
- `research`: research-suite scenario count, sensitivity sweep size, report
  figure formats, interactive-output toggle, empirical completeness threshold,
  maximum report figure count, and stack-synthesis validation, artifact, and
  scholarship thresholds.

## Examples

Run a faster low-resolution animation pass while keeping the scientific defaults
unchanged:

```yaml
beestack:
  visualization:
    animation_frames: 8
    animation_fps: 4
    body_render_width: 320
    body_render_height: 240
    swarm_collision_bee_count: 10
    swarm_collision_radius_m: 0.14
    swarm_collision_initial_speed_m_s: 0.35
    swarm_collision_scene_radius_m: 0.18
    swarm_collision_altitude_m: 0.05
    swarm_collision_min_actual_contact_pairs: 1
    waggle_dance_duration_s: 1.2
    waggle_dance_angle_deg: 35.0
    waggle_dance_sun_azimuth_deg: 120.0
    waggle_dance_quality: 0.8
    waggle_dance_followers: 10
    waggle_dance_waggle_amplitude_m: 0.035
    waggle_dance_loop_radius_m: 0.085
    long_waggle_animation_frames: 96
    long_waggle_animation_fps: 12
    flybody_scene_substeps: 4
  waggle:
    waggle_run_frequency_hz: 13.0
    lateral_amplitude_m: 0.035
    loop_radius_m: 0.085
    follower_spacing_m: 0.11
    follower_orientation_gain: 0.65
    antennal_sampling_gain: 0.75
    stop_signal_sensitivity: 1.0
    max_orientation_error_deg: 90.0
    orientation_error_target_deg: 35.0
    orientation_confidence_target: 0.65
  niche:
    thermoregulation_gain: 0.24
    seasonal_forage_amplitude: 0.35
    weather_forage_penalty: 0.10
  research:
    scenario_count: 5
    sensitivity_sweep_size: 5
    report_figure_formats: ["png"]
    interactive_outputs: true
    empirical_completeness_threshold: 0.5
    max_report_figures: 32
    synthesis_validation_target: 0.9
    synthesis_artifact_coverage_target: 1.0
    synthesis_min_scholarship_refs: 7
```

Point BeeStack at a local FlyBody fork and use a custom action dimension if the
fork changes the actuator set:

```yaml
beestack:
  flybody:
    local_fork_path: /absolute/path/to/flybody-beestack
    action_dim_default: 64
```

Limit empirical BeeBrain alignment to one odor template for a small experiment:

```yaml
beestack:
  empirical:
    enabled_dataset_ids:
      - dryad-paoli-2024-al-calcium
    odor_templates:
      - hexanal
```

Validation fails early for impossible rates, invalid dimensions, empty dataset
IDs, non-increasing calcium stimulus windows, impossible collision radii,
nonpositive strict-scene speeds/altitudes/substeps, missing required contact
pairs, invalid waggle-dance quality/follower/amplitude/loop settings, long
waggle settings that are shorter than the base animation, and invalid
waggle-domain frequency, spacing, orientation-gain, antennal-sampling,
stop-signal, orientation-error, confidence-target, thermoregulation,
seasonal-forage, and weather-penalty settings. Unsafe body-plan output
subdirectories also fail. Research-suite validation rejects empty report
formats, sensitivity sweeps with fewer than two values, invalid empirical
completeness thresholds, nonpositive report-figure limits, invalid synthesis
validation/artifact coverage targets, and negative scholarship-reference
minimums.
