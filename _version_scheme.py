"""
Build-time version resolution via plain git commands.

Executed by hatchling's ``code`` source to stamp ``__version__`` into the
wheel metadata.  Not shipped inside the package — at runtime, version
information is read from ``importlib.metadata``.

Version format (PEP 440):
  - Exact tag  (distance == 0):  X.Y.Z
  - Untagged commit:             X.Y.Z.devN+<branch-slug>

Branch slug rules (PEP 440 local-version label):
  - Every character outside [a-zA-Z0-9] → replaced by "."
  - Leading/trailing dots stripped
  - PEP 440 normalises all separators to "." anyway, so writing dots
    directly keeps the computed version and the wheel filename identical.

Examples:
  develop              →  2.3.4.dev5+develop
  feat/my-feature      →  2.3.4.dev5+feat.my.feature
  IAGC-594             →  2.3.4.dev5+IAGC.594

CI / detached HEAD:
  When git returns "HEAD", the $version environment variable is used
  as fallback (set it to $CI_COMMIT_REF_NAME on GitLab or
  ${GIT_BRANCH#origin/} on Jenkins before invoking the build).

Note on tags: this project uses plain X.Y.Z tags (no "v" prefix).
"""

from __future__ import annotations

import os
import re
import subprocess


def _git(*args: str) -> str:
    return (
        subprocess.check_output(
            ["git", *args],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL,
        )
        .decode()
        .strip()
    )


def _slugify_branch(branch: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", ".", branch).strip(".")


def compute_version() -> str:
    try:
        describe = _git("describe", "--tags", "--long")
    except subprocess.CalledProcessError:
        return "0.0.0.dev0"

    m = re.match(r"^(.+)-(\d+)-g[0-9a-f]+$", describe)
    if not m:
        return "0.0.0.dev0"

    raw_tag = m.group(1).lstrip("v")
    distance = int(m.group(2))

    if distance == 0:
        return raw_tag

    try:
        branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    except subprocess.CalledProcessError:
        branch = ""

    if not branch or branch == "HEAD":
        branch = os.environ.get("version", "")

    slug = _slugify_branch(branch) if branch and branch != "HEAD" else ""
    base = f"{raw_tag}.dev{distance}"
    return f"{base}+{slug}" if slug else base


__version__: str = compute_version()
