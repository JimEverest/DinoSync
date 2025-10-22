# 开发指南

**项目:** dinox-api  
**版本:** v0.2.0

---

## 快速开始

### 1. 环境配置

```bash
# 克隆项目
git clone https://github.com/JimEverest/DinoSync.git
cd DinoSync

# 安装依赖
pip install -r requirements.txt

# 配置Token
cp env.example .env
# 编辑 .env 文件，添加你的 DINOX_API_TOKEN
```

### 2. 运行测试

```bash
# 完整测试套件
pytest test_dinox_client.py -v

# 健康检查
python health_check.py

# 示例代码
python example.py
```

---

## 测试

### 测试套件

| 测试文件 | 用途 | 运行命令 |
|---------|------|---------|
| `test_dinox_client.py` | 主测试套件(22个测试) | `pytest test_dinox_client.py -v` |
| `health_check.py` | API健康检查 | `python health_check.py` |
| `example.py` | 功能演示 | `python example.py` |

### 测试覆盖率

```bash
pytest test_dinox_client.py --cov=dinox_client --cov-report=html
```

### 配置测试Token

```bash
# Linux/Mac
export DINOX_API_TOKEN="your_token"

# Windows PowerShell
$env:DINOX_API_TOKEN="your_token"

# 或创建 .env 文件
echo "DINOX_API_TOKEN=your_token" > .env
```

---

## 发布到 PyPI

### 1. 更新版本

```python
# dinox_client.py
__version__ = "0.x.0"

# setup.py
version="0.x.0"

# pyproject.toml
version = "0.x.0"
```

### 2. 更新 CHANGELOG

```markdown
## [v0.x.0] - YYYY-MM-DD

### 新增
- Feature 1
- Feature 2

### 修复
- Bug fix 1
```

### 3. 构建包

```bash
# 安装构建工具
pip install --upgrade build twine

# 构建
python -m build

# 检查
twine check dist/*
```

### 4. 发布

```bash
# 测试环境（可选）
twine upload --repository testpypi dist/*

# 生产环境
twine upload dist/*
# 或使用token:
twine upload dist/* --username __token__ --password pypi-YOUR_TOKEN
```

### 5. 验证

```bash
# 创建新环境测试
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
test_env\Scripts\activate  # Windows

# 安装测试
pip install dinox-api==0.x.0

# 验证
python -c "from dinox_client import __version__; print(__version__)"
```

---

## 代码规范

### 格式化

```bash
# 使用 black (可选)
pip install black
black dinox_client.py

# 检查 (可选)
pip install flake8
flake8 dinox_client.py
```

### 类型检查

```bash
# 使用 mypy (可选)
pip install mypy
mypy dinox_client.py
```

---

## 项目结构

```
dinox_api_py/
├── dinox_client.py         # 核心库
├── test_dinox_client.py    # 测试套件
├── health_check.py         # 健康检查
├── example.py              # 使用示例
├── setup.py                # PyPI配置
├── pyproject.toml          # 现代打包配置
├── requirements.txt        # 依赖
├── README.md               # 主文档
├── API.md                  # API参考
├── CHANGELOG.md            # 版本历史
└── DEVELOPMENT.md          # 本文件
```

---

## 故障排查

### 测试失败

```bash
# 查看详细错误
pytest test_dinox_client.py -v --tb=short

# 单个测试
pytest test_dinox_client.py::test_get_notes_list -v
```

### 导入错误

```python
# 确认模块可导入
python -c "import dinox_client; print(dinox_client.__version__)"
```

### 网络问题

```bash
# 测试连接
curl -I https://dinoai.chatgo.pro
curl -I https://aisdk.chatgo.pro
```

---

## 贡献

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing`)
5. 创建 Pull Request

---

## 监控上游API变化

### 定期检查（推荐每周）

```bash
# 1. 运行健康检查
python health_check.py

# 2. 保存快照
cp snapshots/current_snapshot.json snapshots/snapshot_$(date +%Y%m%d).json

# 3. 对比变化
diff snapshots/baseline.json snapshots/current_snapshot.json
```

### 发现API变更时的操作清单

- [ ] 运行 `python health_check.py` 确认问题
- [ ] 更新 TROUBLESHOOTING.md 的"当前API状态"和"已知问题"
- [ ] 记录错误信息和服务器响应
- [ ] 评估影响：核心功能 vs 次要功能
- [ ] 决策：紧急修复 vs 计划修复 vs 标记已知问题
- [ ] 更新测试用例（标记预期错误）
- [ ] 更新 API.md 状态说明
- [ ] 发布新版本（如需要）

### 应急响应场景

**场景1: 核心端点404**
```bash
python health_check.py           # 确认
grep "404" TROUBLESHOOTING.md    # 查是否已知
# 如是新问题 → 立即更新TROUBLESHOOTING.md已知问题列表
```

**场景2: 认证失败**
```bash
# 验证Token
python -c "print('TOKEN_LEN:', len('$DINOX_API_TOKEN'))"
# 检查格式（JWT应该是三段: xxx.yyy.zzz）
```

**场景3: 响应结构变化**
```bash
# 对比快照找出差异
diff snapshots/baseline.json snapshots/current_snapshot.json
```

---

## 常见任务

### 添加新API方法

1. 在 `dinox_client.py` 中添加方法
2. 添加到 `METHOD_SERVER_MAP` (如需自动路由)
3. 在 `test_dinox_client.py` 添加测试
4. 更新 `API.md`
5. 更新 `CHANGELOG.md`

### 修复Bug

1. 创建复现测试
2. 修复代码
3. 验证测试通过
4. 更新 `CHANGELOG.md`

### 发现上游API变更

1. 运行健康检查记录状态
2. 更新 TROUBLESHOOTING.md 端点状态矩阵
3. 添加到已知问题列表（如果是问题）
4. 更新测试用例
5. 决定是否需要代码修改

---

**更多问题:** 查看 README.md 或提交 Issue
