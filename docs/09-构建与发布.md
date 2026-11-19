# 构建、发布与安装

本文说明如何把 viseron-qqbotpy 构建成标准 Python 分发包，并发布到 PyPI，让用户可以通过 pip 直接安装。

## 1. 三种使用方式

### 1.1 从源码文件夹安装

在项目根目录执行：

    cd viseron-botpy
    pip install -e .

其中 -e 是开发模式，代码修改后立即生效。

不使用 -e 则是普通安装：

    pip install .

### 1.2 从构建产物安装

构建完成后，可以直接安装 dist 目录中的 wheel 文件：

    pip install dist/viseron_qqbotpy-0.3.0-py3-none-any.whl

也可以安装源码包：

    pip install dist/viseron_qqbotpy-0.3.0.tar.gz

### 1.3 从 PyPI 安装

发布到 PyPI 后，用户只需要执行：

    pip install viseron-qqbotpy

## 2. 构建示例

### 2.1 安装构建工具

只需要安装一次：

    python -m pip install build twine

说明：

- build 用于生成 sdist 源码包和 wheel 二进制包。
- twine 用于检查并上传分发包。

### 2.2 清理旧产物

可选，但推荐：

    rm -rf dist build src/viseron_qqbotpy.egg-info

Windows PowerShell 使用：

    Remove-Item -Recurse -Force dist, build, src\viseron_qqbotpy.egg-info -ErrorAction SilentlyContinue

### 2.3 执行构建

在项目根目录 viseron-botpy 下执行：

    python -m build

构建成功后，会在 dist 目录生成两个文件：

- viseron_qqbotpy-0.3.0-py3-none-any.whl
- viseron_qqbotpy-0.3.0.tar.gz

示例输出末尾类似：

    Successfully built viseron_qqbotpy-0.3.0.tar.gz and viseron_qqbotpy-0.3.0-py3-none-any.whl

### 2.4 检查构建产物

上传前建议检查：

    python -m twine check dist/*

通过时会显示：

    Checking dist/viseron_qqbotpy-0.3.0-py3-none-any.whl: PASSED
    Checking dist/viseron_qqbotpy-0.3.0.tar.gz: PASSED

## 3. 发布到 TestPyPI

正式发布前，建议先发布到 TestPyPI 验证。

### 3.1 注册账号

访问 https://test.pypi.org 注册测试账号，并创建 API Token。

### 3.2 配置上传凭据

方式一：使用环境变量。

Linux / macOS：

    export TWINE_USERNAME=__token__
    export TWINE_PASSWORD=pypi-你的token

Windows PowerShell：

    $env:TWINE_USERNAME = "__token__"
    $env:TWINE_PASSWORD = "pypi-你的token"

方式二：创建 .pypirc 文件。

在用户主目录创建 .pypirc：

    [distutils]
    index-servers =
        pypi
        testpypi

    [pypi]
    username = __token__
    password = pypi-你的正式token

    [testpypi]
    repository = https://test.pypi.org/legacy/
    username = __token__
    password = pypi-你的测试token

注意：.pypirc 包含密钥，不要提交到 Git。

### 3.3 上传到 TestPyPI

    python -m twine upload --repository testpypi dist/*

### 3.4 从 TestPyPI 测试安装

    pip install -i https://test.pypi.org/simple/ viseron-qqbotpy

## 4. 正式发布到 PyPI

### 4.1 注册并创建正式 Token

访问 https://pypi.org 注册账号，创建正式 API Token。

### 4.2 更新版本号

每次发布前，至少修改两个文件中的版本号：

- viseron-botpy/pyproject.toml 中的 version
- viseron-botpy/src/viseron_qqbotpy/__init__.py 中的 __version__

例如从 0.2.0 升级到 0.3.0：

pyproject.toml：

    version = "0.3.0"

__init__.py：

    __version__ = "0.3.0"

### 4.3 重新构建并检查

    python -m build
    python -m twine check dist/*

### 4.4 上传到 PyPI

    python -m twine upload dist/*

### 4.5 发布后安装验证

    pip install viseron-qqbotpy

### 4.6 归档版本（Git tag）

发布完成后，把同一份代码提交并打上 Git tag，方便回溯每个发布版本：

    git add -A
    git commit -m "release: v0.3.0"
    git tag -a v0.3.0 -m "v0.3.0"
    git push origin main
    git push origin v0.3.0

tag 名与 pyproject.toml 中的 version 保持一致，例如 0.3.0 对应 v0.3.0。

## 5. 发布流程总结

完整流程如下：

    cd viseron-botpy

    # 1. 修改版本号
    # 编辑 pyproject.toml 和 src/viseron_qqbotpy/__init__.py

    # 2. 清理旧产物
    rm -rf dist build src/viseron_qqbotpy.egg-info

    # 3. 构建
    python -m build

    # 4. 检查
    python -m twine check dist/*

    # 5. 先上传测试源
    python -m twine upload --repository testpypi dist/*

    # 6. 测试安装
    pip install -i https://test.pypi.org/simple/ viseron-qqbotpy

    # 7. 验证无误后上传正式源
    python -m twine upload dist/*

    # 8. 提交并打 tag
    git add -A
    git commit -m "release: v0.3.0"
    git tag -a v0.3.0 -m "v0.3.0"
    git push origin main
    git push origin v0.3.0

## 6. 常见问题

### 6.1 包名被占用

如果 viseron-qqbotpy 在 PyPI 上已被占用，需要修改 pyproject.toml 中的 name 字段：

    name = "viseron-qqbotpy-你的后缀"

注意：distribution name 可以和 Python import 名不同。修改 name 只影响 pip install 的名称，不影响代码中的 import viseron_qqbotpy。

### 6.2 构建时缺少工具

报错提示 No module named build 时：

    python -m pip install build

报错提示 No module named twine 时：

    python -m pip install twine

### 6.3 上传时 403 或认证失败

通常原因：

- Token 错误或已过期。
- 使用正式 PyPI Token 上传到了 TestPyPI，或反过来。
- 包名已经被占用。

先确认 TWINE_USERNAME 是 __token__，TWINE_PASSWORD 是对应平台的 token。

### 6.4 .env 会被打包进去吗

不会。项目通过 src 布局打包，只包含 viseron_qqbotpy 包内的 Python 文件。根目录的 .env、examples、tests、docs 不会进入 wheel 的正常导入路径。

## 7. 当前项目已构建的产物

本文档编写时，已经成功构建并检查通过：

- viseron-botpy/dist/viseron_qqbotpy-0.3.0-py3-none-any.whl
- viseron-botpy/dist/viseron_qqbotpy-0.3.0.tar.gz

可以直接用它们做本地安装测试：

    pip install dist/viseron_qqbotpy-0.3.0-py3-none-any.whl

## 8. 完整手动发布流程（ChatClone-BotPy）

以下步骤必须按顺序执行，每一步成功后再进入下一步。

### 8.1 发布前检查

    cd D:\Program\QQ-Bot-Class\qqbotpy-source-code\viseron-botpy

确认：

- pyproject.toml 的 version 与 src/viseron_qqbotpy/__init__.py 的 __version__ 一致。
- CHANGELOG.md 有对应版本段落。
- git status 干净。
- 版本规则：major 为不兼容/大量新接口；minor 为新增接口或字段；patch 为 bug/文档修正。

### 8.2 使用 ChatClone-BotPy 环境

    $py = 'C:\Users\25639\.conda\envs\ChatClone-BotPy\python.exe'

如果 conda 在 PATH 中，也可以使用 conda run -n ChatClone-BotPy。

### 8.3 测试

    & $py -m pytest -q

要求全部通过，日志保存到 reports/logs/YYYY-MM-DD-pytest.log。

### 8.4 清理并构建

    Remove-Item -Recurse -Force dist, build, src\viseron_qqbotpy.egg-info -ErrorAction SilentlyContinue
    & $py -m build
    & $py -m twine check dist/*

要求两个产物都 PASSED。保存 build 和 twine 日志。

### 8.5 干净环境试装 wheel

    conda create -n verify-qqbotpy python=3.11 -y
    conda run -n verify-qqbotpy python -m pip install dist/viseron_qqbotpy-X.Y.Z-py3-none-any.whl
    conda run -n verify-qqbotpy python -c "import viseron_qqbotpy; print(viseron_qqbotpy.__version__)"

### 8.6 TestPyPI

    $env:TWINE_USERNAME = "__token__"
    $env:TWINE_PASSWORD = "pypi-测试token"
    & $py -m twine upload --repository testpypi dist/*

测试安装：

    conda run -n verify-qqbotpy python -m pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ viseron-qqbotpy==X.Y.Z

### 8.7 正式 PyPI

    $env:TWINE_USERNAME = "__token__"
    $env:TWINE_PASSWORD = "pypi-正式token"
    & $py -m twine upload dist/*

发布后验证：

    pip install --upgrade viseron-qqbotpy
    python -c "import viseron_qqbotpy; print(viseron_qqbotpy.__version__)"

### 8.8 Git 提交与 tag

    git add .
    git commit -m "chore: release vX.Y.Z"
    git tag -a vX.Y.Z -m "viseron-qqbotpy vX.Y.Z"
    git push origin main --tags
    git ls-remote --tags origin

### 8.9 检查清单

- [ ] 两处版本号一致
- [ ] CHANGELOG 已更新
- [ ] pytest 全部通过
- [ ] build 成功
- [ ] twine check 两个产物 PASSED
- [ ] 干净环境 wheel 安装成功
- [ ] TestPyPI 安装成功
- [ ] PyPI 上传成功
- [ ] pip install viseron-qqbotpy 成功
- [ ] tag 已推送
- [ ] GitHub Release 已创建（可选）

### 8.10 常见失败

- 403：Token 错误、平台不匹配或包名被占用。
- File already exists：同版本不能重复上传，必须升版本。
- twine check 失败：检查 README 编码和 pyproject 元数据。
- ModuleNotFoundError：确认使用 ChatClone-BotPy 环境。
- 构建后 import 旧版本：清理 build、egg-info、__pycache__ 后重装。

## 9. GitHub Actions 自动发布（Trusted Publishing）

上面第 8 节是**手动**流程。从 v0.4.1 之后，仓库里也提供了**自动**发布：用 PyPI 的
Trusted Publishing（OIDC 身份联邦），**不需要在 GitHub 里存任何 API Token 或 Secret**。

### 9.1 原理

GitHub Actions 运行时可以申请一个短期 OIDC 身份令牌，PyPI / TestPyPI 校验这个令牌里的
「仓库 + workflow 文件名 + environment 名」，匹配才允许上传。所以：

- 不用 `TWINE_PASSWORD`，也不用把 token 存进仓库 Secret；
- 每次上传的身份是「某个仓库的某个 workflow 在某个 environment 里跑的某次构建」，
  被冒用的风险比长期 token 低；
- 上传时会自动附带 PEP 740 数字证明（attestations）。

### 9.2 两个 workflow

| 文件 | 触发 | 目标 |
|---|---|---|
| `.github/workflows/publish-testpypi.yml` | 手动 `workflow_dispatch`（可选 ref） | TestPyPI |
| `.github/workflows/publish-pypi.yml` | 推送 `v*` tag；或手动指定 tag | 正式 PyPI |

两者的 `build` job 完全一致：装依赖 → `pytest` → `scripts/check_release.py` → `build` →
`twine check` → 上传 artifact；`publish` job 只负责把 artifact 交给 `pypa/gh-action-pypi-publish`。

### 9.3 一次性配置（必须由仓库所有者完成）

发布前要在两个平台各登记一个 **pending publisher**（项目还不存在时也可以先登记）。

**PyPI**（https://pypi.org/manage/account/publishing/）：

| 字段 | 值 |
|---|---|
| PyPI Project Name | `viseron-qqbotpy` |
| Owner | `MCviseron` |
| Repository name | `viseron-qqbotpy` |
| Workflow name | `publish-pypi.yml` |
| Environment name | `pypi` |

**TestPyPI**（https://test.pypi.org/manage/account/publishing/）：

| 字段 | 值 |
|---|---|
| PyPI Project Name | `viseron-qqbotpy` |
| Owner | `MCviseron` |
| Repository name | `viseron-qqbotpy` |
| Workflow name | `publish-testpypi.yml` |
| Environment name | `testpypi` |

> 四个字段必须**逐字**对上，尤其是 workflow 文件名和 environment 名；写错了上传会 403，
> 报错里通常带 `invalid-publisher`。environment 可以另外在仓库 Settings → Environments
> 里创建同名环境（可选加保护规则），不创建也能用。

### 9.4 版本一致性检查

`scripts/check_release.py` 会检查：

1. `pyproject.toml` 的 `version` 与 `src/viseron_qqbotpy/__init__.py` 的 `__version__` 一致；
2. 版本号不含 `+local` 本地标记（PyPI 不接受）；
3. 在 tag 构建中，tag 必须等于 `v<version>`。

本地也可以先跑一遍：

    python scripts/check_release.py
    python scripts/check_release.py --expect-tag v0.4.2

### 9.5 推荐发布流程

1. 改版本号（两处）、更新 CHANGELOG，跑本地测试与构建：

   ```
   python scripts/check_release.py
   python -m pytest -q
   python -m build
   python -m twine check dist/*
   ```

2. 提交并推送 main。
3. 在 GitHub Actions 页面手动跑 **Publish to TestPyPI**，验证上传与打包链路；
   成功后可以 `pip install -i https://test.pypi.org/simple/ viseron-qqbotpy==X.Y.Z` 试装。
4. 打 tag 并推送，自动发正式版：

   ```
   git tag -a vX.Y.Z -m "viseron-qqbotpy vX.Y.Z"
   git push origin vX.Y.Z
   ```

5. 看 Actions 的 **Publish to PyPI** 是否绿色，然后 `pip install --upgrade viseron-qqbotpy` 验证。

### 9.6 常见失败

- `invalid-publisher` / 403：9.3 的四个字段有一个不对，或没登记 pending publisher。
- `id-token` 权限缺失：workflow 的 publish job 必须声明 `permissions: id-token: write`。
- `File already exists`：同名同版本已上传过，升版本；TestPyPI 那条 workflow 开了
  `skip-existing: true`，所以重跑不会炸，正式 PyPI 故意没开。
- tag 与版本不一致：`check_release.py` 会在 build 阶段就失败，不会走到上传。
- environment 名写错：PyPI 侧登记的 environment 与 workflow 里的 `environment.name` 必须一致。

### 9.7 与手动流程的关系

第 8 节的手动流程仍然可用（本地 `twine upload`），适合应急。但正常发版请走 Actions：
手动上传和 Actions 上传对 PyPI 来说是同一件事，**同一版本只能上传一次**，谁先上谁生效。

