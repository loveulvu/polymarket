# Polymarket 预测市场看板

## 项目简介
这是一个基于 Polymarket 数据构建的预测市场看板，采用前后端分离架构，具备数据实时更新、历史数据存储和可视化功能。

## 功能特性
- **实时市场数据**：每 5 分钟自动更新市场数据
- **首页市场卡片**：展示 YES/NO 概率、成交量、差价等信息
- **排序功能**：支持成交量排序和套利排序
- **详情页**：展示市场描述、状态和历史价格图表
- **历史数据可视化**：24H/72H 历史价格折线图
- **YES/NO 概率对比**：直观的概率条展示
- **粒子背景动画**：增强视觉体验
- **卡片 hover 效果**：联动变色效果
- **异常处理**：API 异常时返回缓存数据
- **数据库存储**：本地 MySQL 存储历史数据

## 技术栈
- **前端**：HTML / CSS / JavaScript / Chart.js
- **后端**：Flask / requests / Flask-CORS
- **数据库**：MySQL
- **API**：Polymarket Gamma API / CLOB prices-history API
- **依赖**：flask, flask-cors, requests, mysql-connector-python

## 项目结构
```
polymarket/
├── static/           # 静态资源
│   ├── script.js     # 前端逻辑
│   └── style.css     # 样式文件
├── templates/        # 模板文件
│   ├── index.html    # 首页
│   └── detail.html   # 详情页
├── app.py            # 后端应用
├── init.sql          # 数据库初始化脚本
├── README.md         # 项目文档
└── Polymarket_Local.session.sql  # 数据库会话文件
```

## 启动方式

### 1. 安装依赖
```bash
pip install flask flask-cors requests mysql-connector-python
```

### 2. 数据库准备
- 安装 MySQL 数据库
- 创建数据库 `poly_data`
- 执行 `init.sql` 初始化表结构

### 3. 配置数据库连接
在 `app.py` 中修改数据库连接配置：
```python
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '200412',  # 修改为你的密码
    'database': 'poly_data'
}
```

### 4. 启动后端服务
```bash
python app.py
```

### 5. 访问应用
- 首页：`http://localhost:5000/`
- 详情页：`http://localhost:5000/detail`

## API 接口
- **GET /api/markets**：获取所有市场数据
- **GET /api/history/<token_id>**：获取指定市场的历史价格（从 Polymarket API）
- **GET /api/history/db/<token_id>**：获取指定市场的历史价格（从本地数据库）

## 核心功能
1. **后台数据抓取**：每 5 分钟自动从 Polymarket API 抓取数据
2. **数据存储**：同时存储到实时表和历史表
3. **缓存机制**：减少 API 请求，提高响应速度
4. **异常处理**：API 异常时返回缓存数据
5. **数据可视化**：使用 Chart.js 展示价格趋势

## 后续计划
- 增加市场状态筛选功能
- 支持更多时间维度的历史数据
- 引入搜索和分类筛选
- 增加 watchlist 功能
- 优化前端响应式设计
- 增加用户认证系统
