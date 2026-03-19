# Polymarket 预测市场看板

## 项目简介
这是一个基于 Polymarket 数据构建的预测市场看板。
项目最初是一个带粒子动画背景的前端展示页，后续扩展为具备前后端联动的数据可视化应用。

## 功能特性
- 首页市场卡片展示
- YES / NO 概率显示
- 成交量排序 / 套利排序
- 粒子背景动画
- 卡片 hover 联动变色
- 详情页描述与状态展示
- 24H / 72H 历史价格折线图
- YES / NO 概率对比条
- 后端缓存与接口异常兜底

## 技术栈
- Frontend: HTML / CSS / JavaScript / Chart.js
- Backend: Flask / requests / Flask-CORS
- APIs: Polymarket Gamma API / CLOB prices-history API

## 项目结构
```
project/
├── index.html
├── detail.html
├── script.js
├── app.py
└── ...
```

## 启动方式
1. **安装依赖**
   ```bash
   pip install flask flask-cors requests
   ```

2. **启动后端**
   ```bash
   python app.py
   ```

3. **打开前端页面**
   直接用浏览器打开 index.html ，或通过本地静态服务器访问。

## 已实现功能
- 首页市场数据接入
- 详情页数据联动
- 24H / 72H 历史价格图
- YES / NO 概率条
- 后端缓存
- 异常处理

## 后续计划
- 增加状态筛选
- 提升已结束市场结果判定准确性
- 支持更多时间维度
- 引入搜索和分类筛选
- 增加 watchlist
