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

    pip install dist/viseron_qqbotpy-0.1.0-py3-none-any.whl

也可以安装源码包：

    pip install dist/viseron_qqbotpy-0.1.0.tar.gz

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

- viseron_qqbotpy-0.1.0-py3-none-any.whl
- viseron_qqbotpy-0.1.0.tar.gz

示例输出末尾类似：

    Successfully built viseron_qqbotpy-0.1.0.tar.gz and viseron_qqbotpy-0.1.0-py3-none-any.whl

### 2.4 检查构建产物

上传前建议检查：

    python -m twine check dist/*

通过时会显示：

    Checking dist/viseron_qqbotpy-0.1.0-py3-none-any.whl: PASSED
    Checking dist/viseron_qqbotpy-0.1.0.tar.gz: PASSED

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

例如从 0.1.0 升级到 0.2.0：

pyproject.toml：

    version = "0.2.0"

__init__.py：

    __version__ = "0.2.0"

### 4.3 重新构建并检查

    python -m build
    python -m twine check dist/*

### 4.4 上传到 PyPI

    python -m twine upload dist/*

### 4.5 发布后安装验证

    pip install viseron-qqbotpy

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

- viseron-botpy/dist/viseron_qqbotpy-0.2.0-py3-none-any.whl
- viseron-botpy/dist/viseron_qqbotpy-0.2.0.tar.gz

可以直接用它们做本地安装测试：

    pip install dist/viseron_qqbotpy-0.2.0-py3-none-any.whl
