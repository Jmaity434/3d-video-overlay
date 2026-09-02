# CI/CD and Distribution Plan

## 1. Purpose

This plan defines how `3d-video-overlay` is verified, versioned, released, and
distributed. It distinguishes the current alpha workflow from the controls
needed for a stable public package.

## 2. Current CI Workflow

The repository currently uses GitHub Actions at `.github/workflows/ci.yml`.
It runs on:

- Pushes to `main`.
- Pull requests targeting the repository.

The job uses `ubuntu-latest` and tests Python 3.8, 3.9, 3.10, 3.11, and 3.12.
Each matrix job:

1. Checks out the repository with `actions/checkout@v4`.
2. Installs the selected Python version with `actions/setup-python@v5`.
3. Installs pip and pytest.
4. Installs the project in editable mode with `--no-deps`.
5. Compiles `src` and `tests`.
6. Runs `python -m pytest -q`.

The `--no-deps` choice keeps the current tests lightweight and headless. The
tests validate package metadata and path behavior; they do not create a
Panda3D, Pygame, or ModernGL window or decode a real movie.

## 3. CI Quality Gates

### Required for every change

- Python compilation succeeds.
- Unit tests pass on every supported interpreter.
- No whitespace errors are introduced.
- Package installation resolves the src-layout package.

### Required before a stable release

- Install and test with the declared Panda3D dependency.
- Run a real-media smoke test using a controlled fixture.
- Exercise model success and fallback paths.
- Exercise the runtime in a supported display or controlled off-screen mode.
- Build both sdist and wheel and install them into clean environments.
- Verify README commands from a fresh checkout.

## 4. Recommended CI Evolution

### Stage 1: Improve headless coverage

- Add unit tests for `validate_video_path` type, missing-file, case-insensitive
  extension, and unsupported-extension behavior.
- Mock Panda3D loader boundaries to test video failure wrapping and model
  fallback without requiring a display.
- Add a packaging job that runs `python -m build` and checks wheel contents.

### Stage 2: Runtime integration

- Add a manually triggered or scheduled job with Panda3D installed.
- Use a small legally distributable fixture or generate a fixture under the
  project license.
- Select an explicitly configured Panda3D backend appropriate for the runner.
- Assert that the application can construct, render at least one frame, and
  shut down without hanging.

### Stage 3: Release protection

- Require CI status checks on pull requests.
- Protect `main` from direct unreviewed changes.
- Build artifacts only from version tags.
- Use an environment with restricted publish permissions.

## 5. Versioning Policy

Use Semantic Versioning:

- **MAJOR:** incompatible public API or behavior changes.
- **MINOR:** backward-compatible public features.
- **PATCH:** backward-compatible fixes and documentation corrections.

The version must be updated consistently in:

- `pyproject.toml` under `[project].version`.
- `src/video3doverlay/__init__.py` as `__version__`.
- Release notes or the GitHub release description.

A release should use an annotated Git tag such as `v0.1.0`.

## 6. Distribution Channels

### Current channel: GitHub source

Users can install the current repository with:

```bash
python -m pip install "git+https://github.com/Jmaity434/3d-video-overlay.git"
```

Developers can clone it and install editable mode:

```bash
git clone https://github.com/Jmaity434/3d-video-overlay.git
cd 3d-video-overlay
python -m pip install -e .
```

### Planned channel: PyPI

When a release is ready:

1. Build an sdist and wheel with `python -m build`.
2. Inspect wheel contents and metadata.
3. Publish to TestPyPI using a protected GitHub environment.
4. Install from TestPyPI in a clean environment and run the sample.
5. Publish the same artifacts to PyPI after approval.
6. Create a GitHub release for the matching tag.

The public install command after PyPI publication will be:

```bash
python -m pip install video3doverlay
```

Do not document that command as the primary route until the package has
actually been published and verified on PyPI.

## 7. Release Workflow

```text
Feature branch
    -> pull request
    -> matrix CI and review
    -> merge to main
    -> version update
    -> tag vX.Y.Z
    -> build artifacts
    -> TestPyPI validation
    -> PyPI publish
    -> GitHub release
```

The release job should use trusted publishing or a short-lived token rather
than storing a long-lived PyPI password in repository secrets.

## 8. Artifact and Dependency Policy

- Keep runtime dependency declarations in `pyproject.toml` authoritative.
- Do not commit wheels, sdists, video files, model files, or cache directories.
- Keep `.gitignore` covering Python caches and build outputs.
- Verify the wheel contains `video3doverlay` under the expected package path.
- Treat Panda3D as a runtime dependency even when headless unit tests skip it.

## 9. Observability and Failure Response

CI failures should identify the Python version and failing stage. Runtime
failures should include the affected asset path and preserve the original
exception as a cause. Failed releases must stop before publication; a broken
artifact should never be promoted from TestPyPI to PyPI.

## 10. Distribution Readiness Checklist

- [ ] Version is synchronized in metadata and package code.
- [ ] README install and sample commands work from a clean checkout.
- [ ] Unit and compile checks pass across the supported Python matrix.
- [ ] Panda3D runtime smoke test passes on the supported target platform.
- [ ] sdist and wheel metadata are correct.
- [ ] License is included in source distribution and documented.
- [ ] Git tag matches the package version.
- [ ] TestPyPI installation succeeds.
- [ ] PyPI publication uses protected credentials or trusted publishing.
- [ ] GitHub release notes describe changes and known limitations.
