from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
import json
import traceback
import mysql.connector
from datetime import datetime
import threading
from flask import render_template 
app = Flask(__name__)
CORS(app)

session = requests.Session()

market_cache = {"data": [], "timestamp": 0}
history_cache = {}

MARKET_CACHE_TTL = 30
HISTORY_CACHE_TTL = 120

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '200412',
    'database': 'poly_data'
}

def save_to_mysql(data_list):
    """统一处理数据库写入：同时更新实时表和历史表"""
    if not data_list:
        return

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1. 批量更新实时表 (快照覆盖)
        sql_upsert = """
        INSERT INTO polymarket_prices 
        (question_title, yes_price, no_price, diff_value, volume, token_id) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            yes_price = VALUES(yes_price),
            no_price = VALUES(no_price),
            diff_value = VALUES(diff_value),
            volume = VALUES(volume)
        """
        cursor.executemany(sql_upsert, data_list)

        # 2. 历史数据（带过滤）
        history_data = []

        for row in data_list:
            token_id = row[5]
            current_price = float(row[1])

            # 查询该 token 最近一条历史价格
            cursor.execute(
                "SELECT price FROM market_history WHERE token_id = %s ORDER BY recorded_at DESC LIMIT 1",
                (token_id,)
            )
            result = cursor.fetchone()

            if result:
                last_price = float(result[0])
                # 变化太小就不记录
                if abs(current_price - last_price) <= 0.01:
                    continue

            # 没有历史 或 有明显变化 → 记录
            history_data.append((token_id, current_price))

        # 批量插入历史数据
        if history_data:
            sql_history = "INSERT INTO market_history (token_id, price) VALUES (%s, %s)"
            cursor.executemany(sql_history, history_data)

        conn.commit()

        now = datetime.now()
        print(f"[{now.strftime('%H:%M:%S')}] 实时更新 {len(data_list)} 条，历史新增 {len(history_data)} 条")

    except mysql.connector.Error as err:
        print(f"数据库写入失败: {err}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def update_all_markets():
    """核心抓取与封装逻辑（供前端路由和后台矿工共同调用）"""
    res = session.get(
        "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=30",
        timeout=10
    )
    res.raise_for_status()
    raw_data = res.json()

    markets = []
    db_data_to_save = []

    for m in raw_data:
        question = m.get("question", "").strip()
        if not question:
            continue

        tokens = m.get("tokens", [])
        yes_price = 0.0
        no_price = 0.0
        diff = 0.0

        try:
            if tokens and len(tokens) >= 2:
                yes_price = float(tokens[0].get("price", 0) or 0)
                no_price = float(tokens[1].get("price", 0) or 0)
            elif "outcomePrices" in m and m.get("outcomePrices"):
                prices = json.loads(m["outcomePrices"])
                yes_price = float(prices[0]) if len(prices) > 0 else 0.0
                no_price = float(prices[1]) if len(prices) > 1 else 0.0
            else:
                yes_price = float(m.get("bestBid", 0) or 0)
                no_price = 1 - yes_price if yes_price <= 1 else 0.0
        except Exception:
            pass 

        clob_token_ids = []
        if m.get("clobTokenIds"):
            try:
                clob_token_ids = json.loads(m.get("clobTokenIds", "[]"))
            except Exception:
                pass

        yes_token_id = clob_token_ids[0] if len(clob_token_ids) > 0 else ""
        no_token_id = clob_token_ids[1] if len(clob_token_ids) > 1 else ""
        
        if yes_price > 0 or no_price > 0:
            diff = abs(yes_price - no_price)

        volume = float(m.get("volumeNum", 0) or 0)
        yes_token_id = m.get('id')

        markets.append({
            "id": yes_token_id,
            "conditionId": m.get("conditionId", ""),
            "yesTokenId": yes_token_id,
            "noTokenId": no_token_id,
            "title": question,
            "yes": yes_price,
            "no": no_price,
            "image": m.get("image", ""),
            "pool": volume,
            "total": yes_price + no_price,
            "description": m.get("description", ""),
            "status": "active",
            "resolution": "pending",
            "active": True,
            "closed": False,
            "diff": diff
        })

        db_data_to_save.append((question, yes_price, no_price, diff, volume, yes_token_id))

    # 执行数据库写入
    if db_data_to_save:
        save_to_mysql(db_data_to_save)

    # 更新缓存
    market_cache["data"] = markets
    market_cache["timestamp"] = time.time()
    return markets

@app.route('/api/markets')
def get_markets():
    if time.time() - market_cache["timestamp"] < MARKET_CACHE_TTL:
        return jsonify(market_cache["data"])
    try:
        markets = update_all_markets()
        return jsonify(markets)
    except Exception as e:
        print(f"/api/markets 错误: {e}")
        traceback.print_exc()
        if market_cache["data"]:
            return jsonify(market_cache["data"])
        return jsonify({"error": str(e)}), 500
@app.route('/api/history/db/<token_id>')
def get_db_history(token_id):
    """从我们自己的数据库读取历史点位（用于绘图）"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True) # 返回字典格式，方便前端处理
        
        # 查询该 ID 过去 24 小时的所有点位
        sql = """
            SELECT price, recorded_at 
            FROM market_history 
            WHERE token_id = %s 
            ORDER BY recorded_at ASC
        """
        cursor.execute(sql, (token_id,))
        rows = cursor.fetchall()
        
        # 格式化数据，确保时间戳能被 JS 识别
        history = []
        for row in rows:
            history.append({
                "timestamp": int(row['recorded_at'].timestamp()),
                "price": float(row['price'])
            })
            
        return jsonify(history)
        
    except Exception as e:
        print(f"数据库读取历史失败: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')          
@app.route('/api/history/<token_id>')
def get_history(token_id):
    # 保持原有逻辑不变
    try:
        range_hours = request.args.get("range", "24")
        if range_hours not in ["24", "72"]:
            range_hours = "24"

        cache_key = f"{token_id}_{range_hours}"
        now = time.time()

        if cache_key in history_cache:
            cached = history_cache[cache_key]
            if now - cached["timestamp"] < HISTORY_CACHE_TTL:
                return jsonify(cached["data"])

        fidelity = 24 if range_hours == "24" else 72

        res = session.get(
            "https://clob.polymarket.com/prices-history",
            params={
                "market": token_id,
                "interval": "1h",
                "fidelity": fidelity
            },
            timeout=10
        )
        res.raise_for_status()
        data = res.json()

        history = []
        if "history" in data and isinstance(data["history"], list):
            for point in data["history"]:
                history.append({
                    "timestamp": point.get("t", 0),
                    "price": float(point.get("p", 0) or 0)
                })

        history_cache[cache_key] = {
            "data": history,
            "timestamp": now
        }

        return jsonify(history)

    except Exception as e:
        print(f"/api/history 错误: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
def clean_old_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    sql = "DELETE FROM market_history WHERE recorded_at < NOW() - INTERVAL 3 DAY"
    cursor.execute(sql)
    conn.commit()

    cursor.close()
    conn.close()

def background_scraper():
    """每 5 分钟自动抓取一次数据，无需手动刷新网页"""
    print("后台矿工已启动...")
    while True:
        try:
            with app.app_context():
                
                  update_all_markets()
                  clean_old_data()
        except Exception as e:
            print(f"后台抓取失败: {e}")
        time.sleep(300)

if __name__ == '__main__':
    # 线程启动必须放在 app.run 之前
    threading.Thread(target=background_scraper, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)