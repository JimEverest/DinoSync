# 📦 PyPI 发布设置指南

## 🔑 配置 GitHub Secrets

为了让 GitHub Actions 能够自动发布包到 PyPI，你需要在 GitHub 仓库中添加 PyPI API Token。

### 步骤：

1. **进入仓库设置**
   - 访问: https://github.com/JimEverest/DinoSync
   - 点击 `Settings` 标签

2. **配置 Secrets**
   - 在左侧菜单找到 `Secrets and variables` → `Actions`
   - 点击 `New repository secret`

3. **添加 PyPI Token**
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: `[你的 PyPI API Token]`
   - 点击 `Add secret`
   
   > ⚠️ **重要**: 请使用你自己的 PyPI API Token。可以从 https://pypi.org/manage/account/token/ 获取。

## 🚀 发布流程

### 自动发布（推荐）

1. **创建 GitHub Release**
   - 访问: https://github.com/JimEverest/DinoSync/releases
   - 点击 `Create a new release`
   - 创建新标签（如 `v0.1.0`）
   - 填写发布说明
   - 点击 `Publish release`
   - GitHub Actions 会自动构建并发布到 PyPI

### 手动触发发布

1. **通过 GitHub Actions 界面**
   - 访问: https://github.com/JimEverest/DinoSync/actions
   - 选择 `Publish to PyPI` workflow
   - 点击 `Run workflow`
   - 选择分支并运行

### 本地发布（备用）

如果需要从本地发布：

```bash
# 安装构建工具
pip install build twine

# 构建包
python -m build

# 检查构建结果
twine check dist/*

# 上传到 PyPI（需要输入 token）
twine upload dist/*
```

当提示输入用户名时，输入：`__token__`
当提示输入密码时，输入完整的 token（包括 `pypi-` 前缀）

## ⚠️ 重要提醒

1. **保密性**: PyPI Token 是敏感信息，请勿在代码中直接暴露
2. **权限**: 这个 token 有完整的上传权限，请妥善保管
3. **版本号**: 每次发布需要更新 `setup.py` 和 `pyproject.toml` 中的版本号
4. **测试**: 发布前建议先在 TestPyPI 上测试

## 📝 版本管理

发布新版本前，需要更新以下文件中的版本号：

1. `setup.py` - `version="0.1.0"`
2. `pyproject.toml` - `version = "0.1.0"`
3. 创建对应的 Git tag: `git tag v0.1.0`

## 🧪 测试 PyPI（可选）

如果想先在测试环境验证：

1. 注册 TestPyPI 账号: https://test.pypi.org/
2. 获取 TestPyPI token
3. 添加额外的 GitHub Secret: `TEST_PYPI_API_TOKEN`
4. 修改 workflow 使用 TestPyPI

## 📚 相关链接

- [PyPI 项目页面](https://pypi.org/project/dinox-api/)（发布后可访问）
- [GitHub Actions 状态](https://github.com/JimEverest/DinoSync/actions)
- [PyPI 账户管理](https://pypi.org/manage/account/)
- [PyPI 文档](https://packaging.python.org/)
