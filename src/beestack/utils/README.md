# Utilities

Shared pure helpers used across BeeStack modules. Utilities must stay small,
deterministic, and dependency-light.

`project_relative_path` and `project_relative_payload` only rebase absolute paths
when passed an explicit `project_root`. Without one, they preserve absolute paths;
they never interpret the caller's working directory as the project boundary.
