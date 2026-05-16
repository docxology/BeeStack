"""Adapter boundary for the BeeStack fork of FlyBody.

FlyBody is an Apache-2.0 MuJoCo fruit-fly body model by TuragaLab, Google
DeepMind, and HHMI Janelia. BeeStack uses it as the intended high-fidelity
BeeBody substrate, while keeping this repository lightweight by making the
heavy simulator optional.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Literal

import numpy as np

from ..config import BeeStackConfig
from ..contracts import Action, Observation
from .bee_mjcf import (
    BeeBodyPlanArtifact,
    BeeBodyPlanError,
    validate_bee_body_plan_xml,
    write_modified_bee_body_plan,
)
from .morphology import flybody_to_bee_features
from .simulation import step_body
from .state import BodyState, BodyTelemetry


class FlyBodyUnavailableError(RuntimeError):
    """Raised when high-fidelity FlyBody execution is requested but unavailable."""


@dataclass(frozen=True)
class FlyBodyForkSpec:
    """Repository-level contract for a BeeStack FlyBody fork."""

    upstream_repo: str = "https://github.com/TuragaLab/flybody"
    expected_fork_remote: str = "https://github.com/docxology/flybody-beestack"
    local_path_env: str = "BEESTACK_FLYBODY_PATH"
    license: str = "Apache-2.0"
    core_model: str = "flybody/fruitfly/assets/fruitfly.xml"
    bee_model_target: str = "flybody/bee/assets/apis_mellifera_worker.xml"


@dataclass(frozen=True)
class FlyBodyPatch:
    """One concrete modification to the FlyBody fork."""

    target: str
    operation: str
    rationale: str
    validation: str


@dataclass(frozen=True)
class FlyBodyModificationPlan:
    """Machine-readable BeeBody patch plan for a FlyBody fork."""

    fork: FlyBodyForkSpec
    patches: tuple[FlyBodyPatch, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "fork": asdict(self.fork),
            "patches": [asdict(patch) for patch in self.patches],
        }


@dataclass(frozen=True)
class FlyBodyRuntimeStatus:
    """Runtime availability and execution mode for the FlyBody adapter."""

    importable: bool
    local_fork_exists: bool
    execution_mode: str
    reason: str


def flybody_available() -> bool:
    """Return whether a Python `flybody` installation is importable."""

    return find_spec("flybody") is not None


def action_to_flybody_action(action: Action, flybody_action_dim: int = 59) -> np.ndarray:
    """Map BeeStack action channels into FlyBody's action vector.

    The public FlyBody README demonstrates a walking environment stepped with a
    59-dimensional action vector. BeeStack actions have bee-specific leg, wing,
    mandible, proboscis, and stinger channels. The adapter preserves leg signals
    first, then appends wing and scalar effectors, padding or truncating to the
    FlyBody environment dimension.
    """

    if flybody_action_dim <= 0:
        raise ValueError("flybody_action_dim must be positive")
    scalars = np.array([action.mandibles, action.proboscis, float(action.stinger)], dtype=float)
    bee_vector = np.concatenate([action.legs, action.wings, scalars]).astype(float)
    if bee_vector.size >= flybody_action_dim:
        return bee_vector[:flybody_action_dim]
    out = np.zeros(flybody_action_dim, dtype=float)
    out[: bee_vector.size] = bee_vector
    return out


def action_to_flybody_named_action(
    action: Action,
    action_spec: Any,
    cfg: BeeStackConfig,
    locomotion_mode: Literal["walk", "flight"] = "walk",
) -> np.ndarray:
    """Map BeeStack actions into a FlyBody action spec by actuator name.

    FlyBody's walking action vector starts with claw adhesion and head/abdomen
    channels before leg joints; flight tasks expose wing joints plus a
    wing-beat-pattern user channel. Name-aware mapping keeps BeeStack's typed
    Body action contract aligned with those FlyBody task APIs.
    """

    shape = getattr(action_spec, "shape", None)
    if not shape:
        return action_to_flybody_action(action, cfg.flybody.action_dim_default)
    size = int(np.prod(shape))
    names = flybody_action_names_from_spec(action_spec)
    if len(names) != size:
        return action_to_flybody_action(action, size).reshape(shape)
    out = np.zeros(size, dtype=float)
    for index, name in enumerate(names):
        out[index] = _named_action_value(name, action, cfg, locomotion_mode)
    minimum = getattr(action_spec, "minimum", None)
    maximum = getattr(action_spec, "maximum", None)
    if minimum is not None and maximum is not None:
        out = np.clip(
            out,
            np.asarray(minimum, dtype=float).reshape(-1),
            np.asarray(maximum, dtype=float).reshape(-1),
        )
    return out.reshape(shape)


def flybody_action_names_from_spec(action_spec: Any) -> tuple[str, ...]:
    """Extract tab-delimited FlyBody action channel names from an action spec."""

    raw_name = getattr(action_spec, "name", "")
    if not isinstance(raw_name, str) or not raw_name:
        return ()
    return tuple(name for name in raw_name.split("\t") if name)


def bee_walk_cycle_action(cfg: BeeStackConfig, step_index: int, cycle_steps: int = 24) -> Action:
    """Generate a tripod-gait BeeStack action for visual FlyBody walking review."""

    phase = 2.0 * np.pi * (step_index % max(1, cycle_steps)) / max(1, cycle_steps)
    legs = np.zeros(cfg.body.leg_dof, dtype=float)
    tripod_offsets = (0.0, np.pi, np.pi, 0.0, 0.0, np.pi)
    amplitudes = np.array([0.45, 0.34, 0.42, 0.24], dtype=float)
    for leg_index, offset in enumerate(tripod_offsets):
        base = leg_index * cfg.body.leg_dof_per_leg
        for dof_index in range(cfg.body.leg_dof_per_leg):
            legs[base + dof_index] = amplitudes[dof_index] * np.sin(
                phase + offset + 0.42 * dof_index
            )
    return Action(legs=legs, wings=np.zeros(cfg.body.wing_dof, dtype=float))


def bee_flight_cycle_action(cfg: BeeStackConfig, step_index: int, cycle_steps: int = 24) -> Action:
    """Generate a BeeStack wing action that requests FlyBody WPG flight motion."""

    phase = 2.0 * np.pi * (step_index % max(1, cycle_steps)) / max(1, cycle_steps)
    wings = np.zeros(cfg.body.wing_dof, dtype=float)
    for wing_index in range(4):
        side_phase = phase if wing_index % 2 == 0 else phase + np.pi
        base = wing_index * cfg.body.wing_dof_per_wing
        wings[base : base + 3] = np.array(
            [
                0.22 * np.sin(side_phase),
                0.18 * np.cos(side_phase),
                0.14 * np.sin(side_phase + np.pi / 3.0),
            ],
            dtype=float,
        )
    return Action(legs=np.zeros(cfg.body.leg_dof, dtype=float), wings=wings)


def flybody_action_dim_from_env(env: Any, default: int = 59) -> int:
    """Read a FlyBody environment action dimension from its action spec."""

    if default <= 0:
        raise ValueError("default action dimension must be positive")
    if not hasattr(env, "action_spec"):
        return default
    spec = env.action_spec()
    shape = getattr(spec, "shape", None)
    if not shape:
        return default
    return int(np.prod(shape))


def validate_rendered_frames(frames: list[np.ndarray], min_dynamic_pixels: int = 32) -> None:
    """Validate that FlyBody rendered nonblank, correctly shaped animation frames."""

    if not frames:
        raise ValueError("rendered frames must not be empty")
    if min_dynamic_pixels <= 0:
        raise ValueError("min_dynamic_pixels must be positive")
    first_shape = frames[0].shape
    if len(first_shape) != 3 or first_shape[2] < 3:
        raise ValueError("rendered frames must be RGB/RGBA images")
    for frame in frames:
        if frame.shape != first_shape:
            raise ValueError("rendered frames must have consistent shape")
    if len(frames) > 1:
        changed = int(np.count_nonzero(frames[-1][..., :3] != frames[0][..., :3]))
        if changed < min_dynamic_pixels:
            raise ValueError("rendered frames do not contain enough motion")
    if float(np.std(frames[0][..., :3])) == 0.0:
        raise ValueError("rendered frames appear blank")


def build_flybody_modification_plan(cfg: BeeStackConfig) -> FlyBodyModificationPlan:
    """Build the required FlyBody fork patch plan for BeeBody."""

    patches = [
        FlyBodyPatch(
            target=feature.name,
            operation=f"Modify {feature.flybody_source} -> {feature.bee_target}",
            rationale="Honeybee morphology differs from Drosophila and must be represented in MJCF.",
            validation=feature.validation_signal,
        )
        for feature in flybody_to_bee_features(cfg)
    ]
    patches.extend(
        (
            FlyBodyPatch(
                "fluid_forces",
                "Retune wing fluid-force coefficients for coupled honeybee forewing/hindwing strokes",
                "The BeeStack spec requires figure-eight wing kinematics and hamular coupling.",
                "Hovering remains stable at 230 Hz with finite CoT.",
            ),
            FlyBodyPatch(
                "task_api",
                "Expose BeeStack Observation and Action adapters around FlyBody task environments",
                "The five-module stack needs the same typed 100 Hz I/O boundary across backends.",
                "validate_observation and validate_action pass for every adapter step.",
            ),
            FlyBodyPatch(
                "assets",
                "Add apis_mellifera_worker MJCF, meshes, materials, and actuator groups",
                "BeeBody must ship a reproducible honeybee model target instead of mutating fruitfly.xml in place.",
                "Fork contains bee_model_target and model-card records its source hash.",
            ),
        )
    )
    return FlyBodyModificationPlan(FlyBodyForkSpec(), tuple(patches))


class FlyBodyBeeBackend:
    """High-fidelity BeeBody adapter with deterministic reduced fallback."""

    def __init__(
        self,
        cfg: BeeStackConfig,
        fork_path: Path | None = None,
        allow_reduced_fallback: bool = True,
    ) -> None:
        self.cfg = cfg
        env_path = os.environ.get(FlyBodyForkSpec.local_path_env)
        configured_path = Path(cfg.flybody.local_fork_path) if cfg.flybody.local_fork_path else None
        self.fork_path = fork_path or configured_path or (Path(env_path) if env_path else None)
        self.allow_reduced_fallback = allow_reduced_fallback

    @property
    def available(self) -> bool:
        return flybody_available() or (self.fork_path is not None and self.fork_path.exists())

    def runtime_status(self) -> FlyBodyRuntimeStatus:
        importable = flybody_available()
        fork_exists = self.fork_path is not None and self.fork_path.exists()
        if importable:
            return FlyBodyRuntimeStatus(
                True, bool(fork_exists), "flybody", "flybody package is importable"
            )
        if fork_exists:
            return FlyBodyRuntimeStatus(
                False, True, "fork-path", "local fork path exists but package import is unavailable"
            )
        if self.allow_reduced_fallback:
            return FlyBodyRuntimeStatus(
                False, False, "reduced-fallback", "using deterministic BeeBody fallback"
            )
        return FlyBodyRuntimeStatus(
            False, False, "unavailable", "FlyBody import and local fork are unavailable"
        )

    def modification_plan(self) -> FlyBodyModificationPlan:
        return build_flybody_modification_plan(self.cfg)

    def write_modified_body_plan(self, output_dir: Path) -> BeeBodyPlanArtifact:
        """Write the custom honeybee MJCF body plan used by FlyBody runs."""

        try:
            artifact = write_modified_bee_body_plan(self.cfg, output_dir, self.fork_path)
            validate_bee_body_plan_xml(Path(artifact.xml_path))
            return artifact
        except BeeBodyPlanError as exc:
            raise FlyBodyUnavailableError(str(exc)) from exc

    def create_walk_imitation_env(self) -> Any:
        """Create FlyBody's walking imitation environment when installed."""

        if not flybody_available():
            raise FlyBodyUnavailableError("flybody package is not importable")
        try:
            fly_envs = import_module("flybody.fly_envs")
            return fly_envs.walk_imitation(random_state=np.random.RandomState(self.cfg.seed))
        except Exception as exc:  # pragma: no cover - depends on optional MuJoCo stack
            raise FlyBodyUnavailableError(
                f"FlyBody walk_imitation failed to initialize: {exc}"
            ) from exc

    def create_bee_walk_imitation_env(
        self,
        body_plan_xml_path: Path,
        ref_path: Path | None = None,
        terminal_com_dist: float | None = None,
        joint_filter: float | None = None,
    ) -> Any:
        """Create a FlyBody walking task that loads the custom BeeBody MJCF."""

        if not flybody_available():
            raise FlyBodyUnavailableError("flybody package is not importable")
        terminal_com_dist = (
            self.cfg.flybody.terminal_com_dist if terminal_com_dist is None else terminal_com_dist
        )
        joint_filter = self.cfg.flybody.joint_filter if joint_filter is None else joint_filter
        try:
            composer = import_module("dm_control.composer")
            floors = import_module("dm_control.locomotion.arenas.floors")
            fruitfly = import_module("flybody.fruitfly.fruitfly")
            walk_imitation = import_module("flybody.tasks.walk_imitation")
            trajectory_loaders = import_module("flybody.tasks.trajectory_loaders")
            random_state = np.random.RandomState(self.cfg.seed)
            if ref_path is None:
                traj_generator = trajectory_loaders.InferenceWalkingTrajectoryLoader()
                inference_mode = True
            else:
                traj_generator = trajectory_loaders.HDF5WalkingTrajectoryLoader(
                    path=str(ref_path),
                    random_state=random_state,
                    traj_indices=None,
                )
                inference_mode = False
            task = walk_imitation.WalkImitation(
                walker=fruitfly.FruitFly,
                arena=floors.Floor(),
                traj_generator=traj_generator,
                terminal_com_dist=terminal_com_dist,
                mocap_joint_names=traj_generator.get_joint_names(),
                mocap_site_names=traj_generator.get_site_names(),
                trajectory_sites=False,
                inference_mode=inference_mode,
                force_actuators=self.cfg.flybody.force_actuators,
                disable_wings=self.cfg.flybody.disable_wings_for_walk,
                joint_filter=joint_filter,
                future_steps=self.cfg.flybody.future_steps,
                time_limit=self.cfg.flybody.time_limit_s,
                walker_xml_path=str(body_plan_xml_path),
            )
            return composer.Environment(
                time_limit=self.cfg.flybody.time_limit_s,
                task=task,
                random_state=random_state,
                strip_singleton_obs_buffer_dim=True,
            )
        except Exception as exc:  # pragma: no cover - depends on optional MuJoCo stack
            raise FlyBodyUnavailableError(
                f"BeeBody FlyBody walk_imitation failed to initialize: {exc}"
            ) from exc

    def create_bee_flight_imitation_env(
        self,
        body_plan_xml_path: Path,
        wpg_pattern_path: Path | None = None,
        terminal_com_dist: float | None = None,
        joint_filter: float | None = None,
    ) -> Any:
        """Create FlyBody's WPG flight task with the custom BeeBody MJCF."""

        if not flybody_available():
            raise FlyBodyUnavailableError("flybody package is not importable")
        terminal_com_dist = (
            self.cfg.flybody.flight_terminal_com_dist
            if terminal_com_dist is None
            else terminal_com_dist
        )
        joint_filter = (
            self.cfg.flybody.flight_joint_filter if joint_filter is None else joint_filter
        )
        try:
            composer = import_module("dm_control.composer")
            floors = import_module("dm_control.locomotion.arenas.floors")
            fruitfly = import_module("flybody.fruitfly.fruitfly")
            flight_imitation = import_module("flybody.tasks.flight_imitation")
            trajectory_loaders = import_module("flybody.tasks.trajectory_loaders")
            pattern_generators = import_module("flybody.tasks.pattern_generators")
            random_state = np.random.RandomState(self.cfg.seed)
            task = flight_imitation.FlightImitationWBPG(
                walker=fruitfly.FruitFly,
                arena=floors.Floor(),
                wbpg=pattern_generators.WingBeatPatternGenerator(
                    base_pattern_path=str(wpg_pattern_path) if wpg_pattern_path else None
                ),
                traj_generator=trajectory_loaders.InferenceFlightTrajectoryLoader(),
                terminal_com_dist=terminal_com_dist,
                initialize_qvel=True,
                force_actuators=self.cfg.flybody.force_actuators,
                disable_legs=self.cfg.flybody.disable_legs_for_flight,
                time_limit=self.cfg.flybody.flight_time_limit_s,
                joint_filter=joint_filter,
                future_steps=self.cfg.flybody.flight_future_steps,
                trajectory_sites=False,
                walker_xml_path=str(body_plan_xml_path),
            )
            for site in getattr(task, "_crosshair_sites", ()):
                site.rgba = (0.0, 0.0, 0.0, 0.0)
                site.size = (1e-6,)
            return composer.Environment(
                time_limit=self.cfg.flybody.flight_time_limit_s,
                task=task,
                random_state=random_state,
                strip_singleton_obs_buffer_dim=True,
            )
        except Exception as exc:  # pragma: no cover - depends on optional MuJoCo stack
            raise FlyBodyUnavailableError(
                f"BeeBody FlyBody flight_imitation failed to initialize: {exc}"
            ) from exc

    def step_walk_imitation_env(self, env: Any, action: Action) -> Any:
        """Step a FlyBody walking environment with a mapped BeeStack action."""

        if hasattr(env, "action_spec"):
            fly_action = action_to_flybody_named_action(
                action,
                env.action_spec(),
                self.cfg,
                locomotion_mode="walk",
            )
        else:
            fly_action = action_to_flybody_action(
                action,
                flybody_action_dim_from_env(env, default=self.cfg.flybody.action_dim_default),
            )
        return env.step(fly_action)

    def render_bee_walk_frames(
        self,
        output_dir: Path,
        action: Action | None = None,
        steps: int | None = None,
        camera_id: int | str | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> tuple[list[np.ndarray], BeeBodyPlanArtifact]:
        """Roll out and render a FlyBody BeeBody walking animation."""

        steps = self.cfg.visualization.animation_frames if steps is None else steps
        camera_id = self.cfg.visualization.body_camera_id if camera_id is None else camera_id
        width = self.cfg.visualization.body_render_width if width is None else width
        height = self.cfg.visualization.body_render_height if height is None else height
        if steps <= 0:
            raise ValueError("steps must be positive")
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        body_plan = self.write_modified_body_plan(output_dir)
        env = self.create_bee_walk_imitation_env(Path(body_plan.xml_path))
        policy = _flybody_cycle_policy(self.cfg, env, "walk", steps, explicit_action=action)
        try:
            flybody_utils = import_module("flybody.utils")
            frames = flybody_utils.rollout_and_render(
                env,
                policy,
                n_steps=steps,
                camera_ids=[camera_id],
                width=width,
                height=height,
            )
        except Exception as exc:  # pragma: no cover - depends on optional MuJoCo renderer
            raise FlyBodyUnavailableError(f"FlyBody rollout_and_render failed: {exc}") from exc
        rendered = [np.asarray(frame, dtype=np.uint8) for frame in frames]
        try:
            validate_rendered_frames(
                rendered, min_dynamic_pixels=self.cfg.flybody.min_dynamic_pixels
            )
        except ValueError as exc:
            raise FlyBodyUnavailableError(str(exc)) from exc
        return rendered, body_plan

    def render_bee_flight_frames(
        self,
        output_dir: Path,
        action: Action | None = None,
        steps: int | None = None,
        camera_id: int | str | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> tuple[list[np.ndarray], BeeBodyPlanArtifact]:
        """Roll out and render a FlyBody BeeBody flight animation."""

        steps = self.cfg.visualization.animation_frames if steps is None else steps
        camera_id = self.cfg.visualization.body_camera_id if camera_id is None else camera_id
        width = self.cfg.visualization.body_render_width if width is None else width
        height = self.cfg.visualization.body_render_height if height is None else height
        if steps <= 0:
            raise ValueError("steps must be positive")
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        body_plan = self.write_modified_body_plan(output_dir)
        env = self.create_bee_flight_imitation_env(Path(body_plan.xml_path))
        policy = _flybody_cycle_policy(self.cfg, env, "flight", steps, explicit_action=action)
        try:
            flybody_utils = import_module("flybody.utils")
            frames = flybody_utils.rollout_and_render(
                env,
                policy,
                n_steps=steps,
                camera_ids=[camera_id],
                width=width,
                height=height,
            )
        except Exception as exc:  # pragma: no cover - depends on optional MuJoCo renderer
            raise FlyBodyUnavailableError(
                f"FlyBody flight rollout_and_render failed: {exc}"
            ) from exc
        rendered = [np.asarray(frame, dtype=np.uint8) for frame in frames]
        try:
            validate_rendered_frames(
                rendered, min_dynamic_pixels=self.cfg.flybody.min_dynamic_pixels
            )
        except ValueError as exc:
            raise FlyBodyUnavailableError(str(exc)) from exc
        return rendered, body_plan

    def step(
        self, state: BodyState, action: Action
    ) -> tuple[BodyState, Observation, BodyTelemetry]:
        """Run one BeeBody step through FlyBody when installed, otherwise fallback."""

        if not self.available and not self.allow_reduced_fallback:
            raise FlyBodyUnavailableError(
                "FlyBody is not importable and no BEESTACK_FLYBODY_PATH fork is available."
            )
        next_state, observation, telemetry = step_body(state, action, self.cfg)
        backend = self.runtime_status().execution_mode
        telemetry = BodyTelemetry(
            telemetry.speed_m_s,
            telemetry.wing_power_mw,
            telemetry.walking_power_mw,
            telemetry.cost_of_transport,
            telemetry.actuator_load,
            backend=backend,
        )
        return next_state, observation, telemetry


def adapter_smoke_rollout(
    cfg: BeeStackConfig, action: Action, steps: int = 3
) -> list[dict[str, float | str]]:
    """Run a short adapter rollout for CI without requiring MuJoCo."""

    if steps <= 0:
        raise ValueError("steps must be positive")
    backend = FlyBodyBeeBackend(cfg)
    state = BodyState(np.zeros(3), np.zeros(3), 0.0)
    rows: list[dict[str, float | str]] = []
    for _ in range(steps):
        state, _, telemetry = backend.step(state, action)
        rows.append(
            {
                "x_m": float(state.position_m[0]),
                "energy_j": state.energy_j,
                "speed_m_s": telemetry.speed_m_s,
                "backend": telemetry.backend,
            }
        )
    return rows


def _flybody_cycle_policy(
    cfg: BeeStackConfig,
    env: Any,
    locomotion_mode: Literal["walk", "flight"],
    cycle_steps: int,
    explicit_action: Action | None = None,
):
    action_spec = env.action_spec()
    counter = {"step": 0}

    def policy(_observation):
        step_index = counter["step"]
        counter["step"] += 1
        if explicit_action is not None:
            bee_action = explicit_action
        elif locomotion_mode == "flight":
            bee_action = bee_flight_cycle_action(cfg, step_index, cycle_steps)
        else:
            bee_action = bee_walk_cycle_action(cfg, step_index, cycle_steps)
        return action_to_flybody_named_action(bee_action, action_spec, cfg, locomotion_mode)

    return policy


def _named_action_value(
    name: str,
    action: Action,
    cfg: BeeStackConfig,
    locomotion_mode: Literal["walk", "flight"],
) -> float:
    if name.startswith("adhere_claw"):
        return _adhesion_for_name(name, action, cfg) if locomotion_mode == "walk" else 0.0
    if name.startswith("wing_"):
        return _wing_value_for_name(name, action, cfg)
    if name.startswith(("coxa", "femur", "tibia", "tarsus")):
        return _leg_value_for_name(name, action, cfg)
    if name == "user_0":
        return 0.18 + 0.35 * min(1.0, float(np.max(np.abs(action.wings))))
    if name == "abdomen_abduct":
        return 0.08 * float(np.mean(action.legs)) if locomotion_mode == "walk" else 0.05
    if name == "abdomen":
        return 0.04 if locomotion_mode == "flight" else 0.0
    return 0.0


def _adhesion_for_name(name: str, action: Action, cfg: BeeStackConfig) -> float:
    leg_index = _leg_index_from_name(name)
    if leg_index is None:
        return 0.7
    base = leg_index * cfg.body.leg_dof_per_leg
    swing = min(1.0, abs(float(action.legs[base]))) if base < action.legs.size else 0.0
    return 0.55 + 0.35 * (1.0 - swing)


def _leg_value_for_name(name: str, action: Action, cfg: BeeStackConfig) -> float:
    leg_index = _leg_index_from_name(name)
    if leg_index is None:
        return 0.0
    base = leg_index * cfg.body.leg_dof_per_leg
    channels = action.legs[base : base + cfg.body.leg_dof_per_leg]
    if channels.size == 0:
        return 0.0
    if name.startswith(("coxa_abduct", "coxa_twist", "coxa_")):
        return float(channels[0])
    if name.startswith(("femur_twist", "femur_")):
        return float(channels[min(1, channels.size - 1)])
    if name.startswith("tibia_"):
        return float(channels[min(2, channels.size - 1)])
    return float(channels[-1])


def _wing_value_for_name(name: str, action: Action, cfg: BeeStackConfig) -> float:
    side_offset = 0 if name.endswith("_left") else cfg.body.wing_dof_per_wing
    hind_offset = 2 * cfg.body.wing_dof_per_wing + (
        0 if name.endswith("_left") else cfg.body.wing_dof_per_wing
    )
    axis_index = 0
    if "_roll_" in name:
        axis_index = 1
    elif "_pitch_" in name:
        axis_index = 2
    fore = action.wings[side_offset + axis_index]
    hind = (
        action.wings[hind_offset + axis_index]
        if hind_offset + axis_index < action.wings.size
        else fore
    )
    return float(0.55 * fore + 0.45 * hind)


def _leg_index_from_name(name: str) -> int | None:
    leg_order = ("T1_left", "T1_right", "T2_left", "T2_right", "T3_left", "T3_right")
    for index, token in enumerate(leg_order):
        if token in name:
            return index
    return None
