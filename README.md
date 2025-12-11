# 期末速通工具 (Exam Helper) 🚀

这是一个基于 **FastAPI** + **DeepSeek LLM** 的智能刷题工具。它可以帮你把乱糟糟的复习资料（文本）一键转换成可以交互的题库（单选、多选、填空），助你期末考试轻松过关！💯

## ✨ 功能特点

*   **🤖 AI 智能解析**: 只要粘贴题目文本，AI 自动识别单选、多选、填空题。
*   **📝 三种题型支持**:
    *   **单选题**: 自动判断对错。
    *   **多选题**: 支持多项选择验证。
    *   **填空题**: 支持多个空的自动比对。
*   **💾 本地题库管理**: 解析后的题目会自动保存，随时回顾。
*   **🎨 沉浸式刷题体验**: 简洁美观的界面，支持“偷看答案”模式。
*   **🔐 简单登录系统**: 保护你的私人题库。

## 🛠️ 技术栈

*   **Backend**: Python, FastAPI
*   **AI**: OpenAI SDK (DeepSeek V3)
*   **Frontend**: HTML5, Tailwind CSS, JavaScript (SPA)

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/exam-helper.git
cd exam-helper
```

### 2. 环境准备
推荐使用 Python 3.8+
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API Key
在项目根目录创建一个 `.env` 文件，填入你的 DeepSeek API Key：
```ini
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. 运行项目
```bash
python main.py
```
然后打开浏览器访问：`http://127.0.0.1:8000`

### 5. 登录
*   用户名: `student`
*   密码: `123123`

---

## ⚠️ License / 许可说明

本项目采用 **自定义非商业许可 (Custom Non-Commercial License)**。

*   ✅ **允许**: 个人学习、研究、非盈利教育用途。
*   ❌ **禁止**: 未经授权的**任何形式的商业用途**（包括但不限于售卖、作为付费服务的一部分等）。

如需**商业授权**，请联系作者。

Copyright (c) 2025. All Rights Reserved.
