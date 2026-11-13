"""发布前的一致性检查（CI 与本地共用）。

检查项：
1. pyproject.toml 的 version 与 src/viseron_qqbotpy/__init__.py 的 __version__ 一致；
2. 版本号不带本地标记（+local），PyPI 不接受；
3. 若在 GitHub Actions 的 tag 构建中（GITHUB_REF_TYPE=tag），tag 必须等于 v<version>。

用法：
    python scripts/check_release.py
    python scripts/check_release.py --expect-tag v0.4.1

退出码 0 表示通过，1 表示不一致。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
INIT = ROOT / "src" / "viseron_qqbotpy" / "__init__.py"


def read_versions() -> tuple[str, str]:
    version = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
    match = re.search(r'__version__\s*=\s*"([^"]+)"', INIT.read_text(encoding="utf-8"))
    if match is None:
        raise SystemExit(f"找不到 __version__：{INIT}")
    return version, match.group(1)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expect-tag",
        default=None,
        help="期望的 tag；默认取环境变量 GITHUB_REF_NAME（仅当 GITHUB_REF_TYPE=tag 时校验）",
    )
    args = parser.parse_args(argv)

    version, init_version = read_versions()
    problems: list[str] = []

    if version != init_version:
        problems.append(
            f"版本号不一致：pyproject.toml={version!r} / __init__.py={init_version!r}"
        )

    if "+" in version:
        problems.append(f"版本号含本地标记，PyPI 不接受：{version!r}")

    tag = args.expect_tag
    if tag is None and os.environ.get("GITHUB_REF_TYPE") == "tag":
        tag = os.environ.get("GITHUB_REF_NAME")

    if tag and tag != f"v{version}":
        problems.append(f"tag 与版本号不匹配：tag={tag!r} 期望 'v{version}'")

    print(f"pyproject version : {version}")
    print(f"__init__ version  : {init_version}")
    print(f"tag               : {tag or '(未校验)'}")

    if problems:
        print("\n检查未通过：", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print("\nOK: 版本一致，可以构建发布。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
