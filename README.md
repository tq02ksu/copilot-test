# Copilot 测试项目

本仓库包含多个示例服务项目，用于演示不同技术栈的应用开发。

## 📦 项目列表

### 1. 🌦️ MCP 天气服务（`mcp-weather-http`）

一个基于 [OpenWeather API](https://openweathermap.org/api) 的**实时天气查询服务端**，兼容 [MCP 协议](https://mcp.chat)，支持流式响应（SSE）和 JSON 响应。

项目采用 `src/` 源码结构，推荐使用 [`uv`](https://github.com/astral-sh/uv) 管理依赖。

### 2. 👥 用户管理服务（`user-service`）

基于 Spring Boot 3.x 的用户管理 REST API 服务，连接 MySQL 数据库，提供完整的用户 CRUD 操作。

- 技术栈：Spring Boot 3.2.2, Spring Data JPA, MySQL 8.0
- 查看详细文档：[user-service/README.md](user-service/README.md)

---

## MCP 天气服务详细说明

## 🚀 功能简介

* 提供一个 LLM 可调用的 MCP 工具：`get-weather`
* 查询指定城市的实时天气（中文描述 + 摄氏温度）
* 流式返回日志、错误与最终结果
* 支持 JSON 响应或 SSE 流式输出
* 使用 [`httpx`](https://www.python-httpx.org/)、[`starlette`](https://www.starlette.io/)、[`click`](https://click.palletsprojects.com/) 构建
* 可通过命令行启动，灵活配置运行参数

---

## 📦 安装方式

### ✅ 使用 [`uv`](https://github.com/astral-sh/uv)（推荐）

```bash
uv pip install -e .
```

### 🧪 或标准安装方式

```bash
pip install -e .
```

---

## ▶️ 启动服务

使用项目中配置的命令行脚本（通过 `pyproject.toml` 提供）：

```bash
mcp-get-weather --port 3000 --api-key YOUR_OPENWEATHER_API_KEY
```

或者手动运行模块：

```bash
python -m src.mcp_get_weather --api-key YOUR_OPENWEATHER_API_KEY
```

---

## ⚙️ 启动参数说明

| 参数                | 描述                                      | 默认值     |
| ----------------- | --------------------------------------- | ------- |
| `--port`          | 服务监听端口                                  | `3000`  |
| `--api-key`       | OpenWeather 的 API 密钥（**必填**，也可通过环境变量提供） | 无默认     |
| `--log-level`     | 日志等级（`DEBUG`, `INFO`, `WARNING` 等）      | `INFO`  |
| `--json-response` | 是否使用 JSON 响应，若不指定则使用 SSE 流式返回           | `False` |

**设置 API 密钥示例**（推荐方式）：

```bash
export OPENWEATHER_API_KEY=your_actual_api_key
```

---

## 🧠 MCP 工具定义

服务向客户端暴露以下工具：

```json
{
  "name": "get-weather",
  "description": "查询指定城市的实时天气（OpenWeather 数据）",
  "inputSchema": {
    "type": "object",
    "required": ["location"],
    "properties": {
      "location": {
        "type": "string",
        "description": "城市的英文名称，如 'Beijing'"
      }
    }
  }
}
```

---

## 📡 返回结果示例

```
Beijing：多云，温度 28.4°C，体感 30.1°C，湿度 55%。
```

---

## 🛠️ 项目结构

```
.
├── src/
│   └── mcp_get_weather/
│       ├── __init__.py  # 主入口
│       ├── __main__.py  
│       ├── server.py  
├── pyproject.toml       # 项目元数据和安装配置
└── README.md
```

`pyproject.toml` 中配置了 CLI 命令 `mcp-get-weather`，指向 `main()` 函数。

---

## 🔐 安全说明

* 服务运行在 Starlette 的 ASGI 框架中，使用 GitHub MCP 协议进行会话管理
* 服务默认无状态（`stateless=True`），不存储历史事件
* 所有请求需通过 `/mcp` 路径进行（符合 MCP 协议）

---

## 💻 开发建议

### 🧪 本地调试

使用 [Uvicorn](https://www.uvicorn.org/) 启动开发服务器：

```bash
uvicorn src.mcp_get_weather:main
```

或运行模块：

```bash
python -m src.mcp_get_weather --api-key $OPENWEATHER_API_KEY
```

---

## 📄 `pyproject.toml` 关键配置

```toml
[project]
name = "mcp-weather-http"
version = "1.1.2"
description = "输入OpenWeather-API-KEY，获取天气信息。"
dependencies = ["httpx>=0.28.1", "mcp>=1.8.0"]

[project.scripts]
mcp-get-weather = "mcp_get_weather:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

---

## 📄 License

本项目用于学习与演示用途。请确保在遵循 [OpenWeather API 使用条款](https://openweathermap.org/price) 的前提下运行和部署本服务。
