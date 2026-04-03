# Daily Research Tracker - 部署指南

## 系统要求

1. **Python 3.10+** (推荐 3.12)
2. **Git** (用于版本控制和GitHub Actions)
3. **GitHub 账户** (用于GitHub Pages和自动化)

## 快速部署步骤

### 1. 克隆和初始化
```bash
# 克隆仓库
git clone https://github.com/your-username/daily-research-tracker.git
cd daily-research-tracker

# 运行设置脚本 (如果Python可用)
python setup.py
```

### 2. 配置 RSS 源
编辑 `rss_sources.txt` 文件，添加您关注的RSS源：
```
# arXiv 计算机科学分类
http://export.arxiv.org/rss/cs.CL
http://export.arxiv.org/rss/cs.CV
http://export.arxiv.org/rss/cs.AI
http://export.arxiv.org/rss/cs.LG

# 期刊 RSS
https://journals.aps.org/rss/prl
https://www.nature.com/subjects/physics/nphys.rss
```

### 3. 设置研究方向
编辑 `research_directions.md` 文件，定义您的研究兴趣：
```
- 机器学习与深度学习
- 自然语言处理与大语言模型
- 计算机视觉与图像识别
- 人工智能理论
- 量子计算与量子机器学习
```

### 4. 配置 API 密钥 (可选)

#### 本地使用：
```bash
# Windows
set OPENAI_API_KEY=your-api-key
set OPENAI_BASE_URL=https://api.deepseek.com

# Linux/macOS
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://api.deepseek.com
```

#### GitHub Actions 使用：
1. 进入 GitHub 仓库 Settings → Secrets and variables → Actions
2. 添加以下 Secrets：
   - `OPENAI_API_KEY`: 您的DeepSeek API密钥
   - `OPENAI_BASE_URL`: `https://api.deepseek.com`

### 5. 启用 GitHub Pages
1. 进入 GitHub 仓库 Settings → Pages
2. 设置 Source 为 "Deploy from a branch"
3. 设置 Branch 为 "main" 和文件夹 "/website"
4. 点击 Save

### 6. 手动测试工作流
1. 进入 GitHub 仓库 Actions 标签页
2. 选择 "Daily Research Tracker" 工作流
3. 点击 "Run workflow"
4. 选择是否跳过 AI 处理 (首次运行建议不跳过)

## 本地开发测试

### 测试 RSS 抓取 (不依赖 Python)
由于Windows可能存在Python配置问题，您可以使用以下替代方案：

1. **使用 WSL (推荐)**
   - 安装 WSL: `wsl --install`
   - 在WSL中运行所有Python脚本

2. **直接测试网站功能**
   - 网站文件已预置测试数据
   - 直接在浏览器中打开 `website/index.html`

### 验证网站功能
1. 打开 `website/index.html` 文件
2. 确保能看到：
   - 标题和统计数据
   - 3篇示例论文
   - 筛选和搜索功能
   - 论文详情模态框

## GitHub Actions 配置说明

### 工作流程文件
`.github/workflows/daily.yml` 已配置以下功能：
- **定时执行**: 每天 UTC 02:00 (北京时间 10:00) 自动运行
- **手动触发**: 支持指定日期和跳过AI处理
- **多分支部署**:
  - `data` 分支: 存储原始JSONL数据
  - `main` 分支: 存储网站文件
- **错误处理**: 各步骤都有失败处理机制

### 自定义设置
如需修改执行时间，编辑 `daily.yml` 中的cron表达式：
```yaml
schedule:
  - cron: "0 2 * * *"  # 每天UTC 02:00
  # 其他选项:
  # "0 10 * * *"  # 每天UTC 10:00 (北京时间18:00)
  # "0 0 * * 1"   # 每周一UTC 00:00
```

## 故障排除

### Python 相关问题
**问题**: "Python was not found" 或类似错误
**解决方案**:
1. 检查Python是否已安装: `py --version`
2. 如果只有Windows Store版本，运行以下命令禁用别名:
   ```powershell
   # 以管理员身份运行PowerShell
   Get-AppxPackage *Python* | Remove-AppxPackage
   ```
3. 从 python.org 下载并安装Python 3.12+
4. 确保在安装时勾选 "Add Python to PATH"

### RSS 抓取失败
**问题**: 无法获取RSS数据
**解决方案**:
1. 检查 `rss_sources.txt` 中的URL是否有效
2. 验证网络连接和代理设置
3. 尝试使用更稳定的RSS源

### AI 处理失败
**问题**: API调用失败
**解决方案**:
1. 验证API密钥是否正确
2. 检查API服务状态 (DeepSeek等)
3. 调整 `config.yaml` 中的模型参数

### GitHub Pages 不更新
**问题**: 网站没有显示最新数据
**解决方案**:
1. 检查GitHub Actions执行日志
2. 确认 `website/` 目录包含完整文件
3. 等待GitHub Pages缓存刷新 (最多10分钟)

## 高级配置

### 阿里云集成 (可选)
如需阿里云同步，需要:
1. 阿里云OSS账号和存储桶
2. 配置访问密钥
3. 修改 `config.yaml` 添加阿里云配置
4. 扩展工作流文件添加同步步骤

### Obsidian 集成
生成的Markdown文件位于 `obsidian/` 目录：
- 每天生成 `YYYY-MM-DD.md` 文件
- 包含完整论文信息和AI分析
- 可直接导入Obsidian库使用

## 性能优化建议

1. **RSS源管理**
   - 精选高质量的RSS源
   - 避免过多源导致处理时间过长
   - 定期检查源的有效性

2. **API成本控制**
   - 设置合理的阈值分数
   - 考虑使用更经济的模型
   - 监控API使用量

3. **数据存储**
   - 定期清理旧数据文件
   - 使用Git LFS处理大文件
   - 考虑数据库存储方案

## 支持与反馈

如有问题，请:
1. 检查GitHub Actions执行日志
2. 查看 `data/` 目录下的日志文件
3. 在Git仓库提交Issue
4. 参考原始项目文档

## 安全注意事项

1. **API密钥安全**
   - 不要将API密钥提交到公开仓库
   - 使用GitHub Secrets管理敏感信息
   - 定期轮换API密钥

2. **数据隐私**
   - 处理的数据仅包含公开论文信息
   - 不涉及个人隐私数据
   - 符合学术使用规范

3. **系统安全**
   - 保持依赖包更新
   - 定期检查安全漏洞
   - 使用可信的RSS源