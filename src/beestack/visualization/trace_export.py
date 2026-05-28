"""Export BeeStack runs into Bee Swarm Live trace JSON."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from ..body import sample_flybody_waggle_pose_trace
from ..config import BeeStackConfig
from ..orchestrator import initialize_simulation, step_simulation

TraceMode = Literal["reduced", "flybody_waggle", "flybody_waggle_pair", "flybody_waggle_long"]


@dataclass(frozen=True)
class BeeSwarmTraceOptions:
    """Options for Bee Swarm Live trace export."""

    steps: int = 600
    bee_count: int = 120
    flower_patches: int = 24
    world_width: int = 1200
    world_height: int = 680
    hive_x: float = 160.0
    hive_y: float = 350.0
    hive_radius: float = 92.0
    trace_mode: TraceMode = "reduced"


def export_bee_swarm_trace(
    cfg: BeeStackConfig,
    *,
    options: BeeSwarmTraceOptions = BeeSwarmTraceOptions(),
) -> dict[str, Any]:
    """Return a BeeStack trace compatible with Bee Swarm Live UI."""

    if options.steps <= 0:
        raise ValueError("options.steps must be positive")
    if options.bee_count < 3:
        raise ValueError("options.bee_count must be at least 3")
    if options.flower_patches <= 0:
        raise ValueError("options.flower_patches must be positive")
    if options.world_width <= 0 or options.world_height <= 0:
        raise ValueError("world dimensions must be positive")
    if options.hive_radius <= 0:
        raise ValueError("options.hive_radius must be positive")
    if options.trace_mode not in {
        "reduced",
        "flybody_waggle",
        "flybody_waggle_pair",
        "flybody_waggle_long",
    }:
        raise ValueError(f"Unsupported trace mode: {options.trace_mode}")

    rng = np.random.default_rng(cfg.seed + 77)
    dt = float(cfg.timing.control_dt_s)
    state = initialize_simulation(cfg)

    flowers = _initialize_flowers(rng, options)
    bees = _initialize_bees(rng, options)
    flybody_pose_frames = _resolve_flybody_pose_frames(cfg, options)
    flybody_prefix_count = (
        min(len(flybody_pose_frames[0]), len(bees)) if flybody_pose_frames is not None else 0
    )
    previous_flybody_poses: Sequence[tuple[float, float, float, float]] | None = None
    frames: list[dict[str, Any]] = []
    recent_signal_counts: dict[str, int] = {"waggle": 0, "stop": 0, "tremble": 0, "shaking": 0}

    for step_idx in range(options.steps):
        state, record = step_simulation(state, cfg)
        if flybody_pose_frames is not None:
            pose_frame = flybody_pose_frames[step_idx % len(flybody_pose_frames)]
            _apply_flybody_pose_frame(
                bees,
                pose_frame,
                previous_flybody_poses,
                options,
                dt,
            )
            previous_flybody_poses = pose_frame
        _advance_bees(
            bees,
            flowers,
            options,
            rng,
            dt,
            record.recruited_followers,
            start_index=flybody_prefix_count,
        )
        _update_flowers(flowers, bees, dt)
        signals = _frame_signals(step_idx, dt, record)
        for signal in signals:
            signal_type = str(signal["type"])
            recent_signal_counts[signal_type] = recent_signal_counts.get(signal_type, 0) + 1

        frames.append(
            {
                "time": float(step_idx * dt),
                "world": {"w": options.world_width, "h": options.world_height},
                "hive": {"x": options.hive_x, "y": options.hive_y, "r": options.hive_radius},
                "bees": [_frame_bee_payload(bee) for bee in bees],
                "flowers": [_frame_flower_payload(flower) for flower in flowers],
                "signals": signals,
            }
        )

    return {
        "dt": dt,
        "frames": frames,
        "metadata": {
            "trace_kind": "beestack_live_trace",
            "note": (
                "Interoperability trace for Bee Swarm Live UI. "
                "Signal cadence is BeeStack-driven."
            ),
            "trace_mode": options.trace_mode,
            "flybody_waggle_bees": flybody_prefix_count,
            "recent_signal_counts": recent_signal_counts,
            "represented_colony_size": int(cfg.swarm.represented_colony_size),
            "simulated_agents": int(options.bee_count),
        },
    }


def _initialize_flowers(rng: np.random.Generator, options: BeeSwarmTraceOptions) -> list[dict[str, Any]]:
    flowers: list[dict[str, Any]] = []
    for idx in range(options.flower_patches):
        x = float(rng.uniform(options.world_width * 0.38, options.world_width * 0.95))
        y = float(rng.uniform(45.0, options.world_height - 45.0))
        cap = float(rng.uniform(85.0, 140.0))
        flowers.append(
            {
                "id": idx,
                "x": x,
                "y": y,
                "cap": cap,
                "nectar": float(rng.uniform(0.55 * cap, cap)),
                "confidence": float(rng.uniform(0.25, 0.88)),
                "discovered": bool(rng.uniform() > 0.14),
                "regen_rate": float(rng.uniform(0.35, 0.95)),
            }
        )
    return flowers


def _initialize_bees(rng: np.random.Generator, options: BeeSwarmTraceOptions) -> list[dict[str, Any]]:
    states = ("idle", "foraging", "returning", "dancing", "recruit")
    roles = ("idle", "scout", "nectar", "waggle", "returning")
    bees: list[dict[str, Any]] = []
    for idx in range(options.bee_count):
        angle = 2.0 * np.pi * idx / max(1, options.bee_count)
        radius = float(rng.uniform(0.08 * options.hive_radius, 0.95 * options.hive_radius))
        x = options.hive_x + radius * float(np.cos(angle))
        y = options.hive_y + radius * float(np.sin(angle))
        vx = float(rng.uniform(-16.0, 16.0))
        vy = float(rng.uniform(-16.0, 16.0))
        bees.append(
            {
                "id": idx,
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "heading": float(np.arctan2(vy, vx)),
                "state": states[idx % len(states)],
                "role": roles[idx % len(roles)],
            }
        )
    return bees


def _advance_bees(
    bees: list[dict[str, Any]],
    flowers: Sequence[dict[str, Any]],
    options: BeeSwarmTraceOptions,
    rng: np.random.Generator,
    dt: float,
    recruited_followers: int,
    *,
    start_index: int = 0,
) -> None:
    top_targets = sorted(flowers, key=lambda flower: flower["nectar"], reverse=True)[:3]
    for bee in bees[start_index:]:
        bee_id = int(bee["id"])
        target = top_targets[bee_id % len(top_targets)]
        home_dx = options.hive_x - float(bee["x"])
        home_dy = options.hive_y - float(bee["y"])
        forage_dx = float(target["x"]) - float(bee["x"])
        forage_dy = float(target["y"]) - float(bee["y"])
        home_norm = max(np.hypot(home_dx, home_dy), 1.0)
        forage_norm = max(np.hypot(forage_dx, forage_dy), 1.0)

        if bee_id < recruited_followers:
            ax = 0.78 * forage_dx / forage_norm + float(rng.normal(0.0, 0.12))
            ay = 0.78 * forage_dy / forage_norm + float(rng.normal(0.0, 0.12))
            bee["state"] = "foraging"
            bee["role"] = "recruit"
        elif bee_id % 11 == 0:
            ax = 0.74 * home_dx / home_norm + float(rng.normal(0.0, 0.11))
            ay = 0.74 * home_dy / home_norm + float(rng.normal(0.0, 0.11))
            bee["state"] = "returning"
            bee["role"] = "returning"
        elif bee_id % 17 == 0:
            ax = float(rng.normal(0.0, 0.17))
            ay = float(rng.normal(0.0, 0.17))
            bee["state"] = "dancing"
            bee["role"] = "waggle"
        else:
            ax = float(rng.normal(0.0, 0.22))
            ay = float(rng.normal(0.0, 0.22))
            bee["state"] = "idle"
            bee["role"] = "idle"

        vx = 0.93 * float(bee["vx"]) + 24.0 * ax * dt
        vy = 0.93 * float(bee["vy"]) + 24.0 * ay * dt
        speed = float(np.hypot(vx, vy))
        max_speed = 62.0
        if speed > max_speed:
            scale = max_speed / speed
            vx *= scale
            vy *= scale

        x = float(bee["x"]) + vx * dt
        y = float(bee["y"]) + vy * dt
        x = float(np.clip(x, 12.0, options.world_width - 12.0))
        y = float(np.clip(y, 12.0, options.world_height - 12.0))
        if x <= 12.0 or x >= options.world_width - 12.0:
            vx *= -0.55
        if y <= 12.0 or y >= options.world_height - 12.0:
            vy *= -0.55

        bee["x"] = x
        bee["y"] = y
        bee["vx"] = float(vx)
        bee["vy"] = float(vy)
        bee["heading"] = float(np.arctan2(vy, vx if abs(vx) + abs(vy) > 1e-9 else 1.0))


def _resolve_flybody_pose_frames(
    cfg: BeeStackConfig, options: BeeSwarmTraceOptions
) -> tuple[tuple[tuple[float, float, float, float], ...], ...] | None:
    scene_by_mode: dict[TraceMode, Literal["waggle", "waggle_pair", "waggle_long"] | None] = {
        "reduced": None,
        "flybody_waggle": "waggle",
        "flybody_waggle_pair": "waggle_pair",
        "flybody_waggle_long": "waggle_long",
    }
    scene_name = scene_by_mode[options.trace_mode]
    if scene_name is None:
        return None
    return sample_flybody_waggle_pose_trace(cfg, scene_name, frames=options.steps)


def _apply_flybody_pose_frame(
    bees: list[dict[str, Any]],
    pose_frame: Sequence[tuple[float, float, float, float]],
    previous_pose_frame: Sequence[tuple[float, float, float, float]] | None,
    options: BeeSwarmTraceOptions,
    dt: float,
) -> None:
    px_per_meter = 245.0
    for idx, pose in enumerate(pose_frame):
        if idx >= len(bees):
            break
        x_m, y_m, _z_m, heading = pose
        bee = bees[idx]
        target_x = float(np.clip(options.hive_x + x_m * px_per_meter, 12.0, options.world_width - 12.0))
        target_y = float(np.clip(options.hive_y + y_m * px_per_meter, 12.0, options.world_height - 12.0))
        prev_x = float(bee["x"])
        prev_y = float(bee["y"])
        if previous_pose_frame is not None and idx < len(previous_pose_frame):
            prev_pose = previous_pose_frame[idx]
            prev_x = float(
                np.clip(options.hive_x + prev_pose[0] * px_per_meter, 12.0, options.world_width - 12.0)
            )
            prev_y = float(
                np.clip(options.hive_y + prev_pose[1] * px_per_meter, 12.0, options.world_height - 12.0)
            )
        bee["x"] = target_x
        bee["y"] = target_y
        bee["vx"] = float((target_x - prev_x) / max(dt, 1e-6))
        bee["vy"] = float((target_y - prev_y) / max(dt, 1e-6))
        bee["heading"] = float(heading)
        bee["state"] = "dancing" if idx == 0 else "recruit"
        bee["role"] = "waggle" if idx == 0 else "nectar"


def _update_flowers(flowers: list[dict[str, Any]], bees: Sequence[dict[str, Any]], dt: float) -> None:
    for flower in flowers:
        fx = float(flower["x"])
        fy = float(flower["y"])
        forager_count = 0
        for bee in bees:
            if bee["state"] not in {"foraging", "recruit"}:
                continue
            if np.hypot(float(bee["x"]) - fx, float(bee["y"]) - fy) < 40.0:
                forager_count += 1
        nectar = float(flower["nectar"])
        cap = float(flower["cap"])
        regen = float(flower["regen_rate"])
        nectar = max(0.0, min(cap, nectar + regen * dt - 0.36 * forager_count * dt))
        flower["nectar"] = nectar
        flower["confidence"] = float(np.clip(0.2 + 0.8 * (nectar / max(cap, 1e-6)), 0.0, 1.0))
        flower["discovered"] = bool(flower["discovered"] or forager_count > 0)


def _frame_signals(step_idx: int, dt: float, record: Any) -> list[dict[str, Any]]:
    t = float(step_idx * dt)
    signals: list[dict[str, Any]] = []
    recruited = int(record.recruited_followers)
    if recruited > 0:
        signals.append(
            {
                "type": "waggle",
                "t": t,
                "strength": float(np.clip(record.dominant_empirical_alignment, 0.0, 1.0)),
                "recruited_followers": recruited,
            }
        )
    if float(record.mean_pheromone) > 0.004 and step_idx % 9 == 0:
        signals.append(
            {
                "type": "stop",
                "t": t,
                "strength": float(np.clip(record.mean_pheromone * 18.0, 0.0, 1.0)),
            }
        )
    if str(record.selected_policy) == "nurse_brood" and step_idx % 6 == 0:
        signals.append(
            {
                "type": "tremble",
                "t": t,
                "strength": float(np.clip(1.0 - record.energy_j / 80.0, 0.0, 1.0)),
            }
        )
    if str(record.selected_policy) in {"follow_dance", "scout"} and step_idx % 5 == 0:
        signals.append(
            {
                "type": "shaking",
                "t": t,
                "strength": float(np.clip(record.body_speed_m_s / 3.0, 0.0, 1.0)),
            }
        )
    return signals


def _frame_bee_payload(bee: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": int(bee["id"]),
        "x": round(float(bee["x"]), 4),
        "y": round(float(bee["y"]), 4),
        "vx": round(float(bee["vx"]), 4),
        "vy": round(float(bee["vy"]), 4),
        "heading": round(float(bee["heading"]), 6),
        "state": str(bee["state"]),
        "role": str(bee["role"]),
    }


def _frame_flower_payload(flower: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": int(flower["id"]),
        "x": round(float(flower["x"]), 4),
        "y": round(float(flower["y"]), 4),
        "nectar": round(float(flower["nectar"]), 4),
        "cap": round(float(flower["cap"]), 4),
        "confidence": round(float(flower["confidence"]), 6),
        "discovered": bool(flower["discovered"]),
    }
