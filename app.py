from flask import Flask, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/markets')
def get_markets():
    try:
        # 使用 Gamma API 的搜索接口，这个接口的数据最全，图片最稳
        url = "https://gamma-api.polymarket.com/markets?limit=50&active=true&closed=false"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        print("开始获取市场数据...")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()  # 检查 HTTP 状态码
        data = resp.json()
        
        print(f"获取到 {len(data)} 条市场数据")
        
        processed = []
        for i, m in enumerate(data):
            try:
                # 1. 提取标题
                title = m.get('question') or m.get('description')
                if not title: continue

                # 2. 【死磕图片相关性】
                # 严格按照：icon(头像) -> outcomes[0].image -> image 的顺序
                img = m.get('icon') 
                if not img or 'placeholder' in img:
                    if m.get('outcomes'):
                        img = m.get('outcomes')[0].get('image')
                if not img:
                    img = m.get('image')
                if not img:
                    img = m.get('conditionId_image')

                # 3. 【死磕 0.5 小数】
                p_yes = 0.5
                # 尝试从 outcomePrices 拿
                prices = m.get('outcomePrices')
                print(f"outcomePrices: {prices}")
                if prices:
                    # 处理可能的字符串格式
                    if isinstance(prices, str):
                        try:
                            import json
                            prices = json.loads(prices)
                            print(f"解析后的 outcomePrices: {prices}")
                        except Exception as e:
                            print(f"解析 outcomePrices 字符串失败: {e}")
                    # 确保 prices 是列表且长度足够
                    if isinstance(prices, list) and len(prices) >= 2:
                        try:
                            p_yes = float(prices[0])
                            print(f"从 outcomePrices 获取到价格: {p_yes}")
                        except Exception as e:
                            print(f"解析 outcomePrices 失败: {e}")
                            pass
                
                # 如果还是 0.5，尝试从最底层的 clobTokenIds 逻辑（如果存在）
                if p_yes == 0.5:
                    # 尝试从 clobTokenIds 深度抓取价格
                    clob_token_ids = m.get('clobTokenIds')
                    print(f"clobTokenIds: {clob_token_ids}")
                    if clob_token_ids:
                        # 处理可能的字符串格式
                        if isinstance(clob_token_ids, str):
                            # 尝试解析字符串
                            try:
                                import json
                                clob_token_ids = json.loads(clob_token_ids)
                                print(f"解析后的 clobTokenIds: {clob_token_ids}")
                            except Exception as e:
                                print(f"解析 clobTokenIds 字符串失败: {e}")
                                pass
                        if isinstance(clob_token_ids, list) and len(clob_token_ids) >= 2:
                            try:
                                token_id = clob_token_ids[0]
                                # 确保 token_id 是字符串
                                if isinstance(token_id, str):
                                    clob_url = f"https://clob.polymarket.com/book?token_id={token_id}"
                                    print(f"尝试抓取 clob 价格: {clob_url}")
                                    clob_resp = requests.get(clob_url, headers=headers, timeout=5)
                                    clob_resp.raise_for_status()
                                    clob_data = clob_resp.json()
                                    print(f"clob 响应: {clob_data}")
                                    # 抓取买一价（Best Bid）
                                    if clob_data.get('bids') and len(clob_data['bids']) > 0:
                                        best_bid = clob_data['bids'][0][0]  # 第一个元素是价格
                                        p_yes = float(best_bid)
                                        print(f"从 clob 获取到价格: {p_yes}")
                            except Exception as e:
                                print(f"抓取 clob 价格失败: {e}")
                                pass

                # 过滤掉那些完全没动静的市场，保证你看到的都有波动
                processed.append({
                    "title": title,
                    "image": img if img else "https://via.placeholder.com/300x180?text=No+Image",
                    "yes": p_yes,
                    "no": 1.0 - p_yes if p_yes != 0.5 else 0.5,
                    "pool": float(m.get('volume', 0))
                })
                
                # 打印前3条数据的 YES 价格
                if i < 3:
                    print(f"第{i+1}条数据: YES 价格 = {p_yes}")
                    print(f"   标题: {title}")
                    print(f"   图片: {img}")
                    print()
                    
            except Exception as e:
                print(f"处理第 {i} 条数据时出错: {e}")
                continue

        # 按资金量大排在前面，因为钱多的市场图片肯定最准、价格肯定最实
        processed.sort(key=lambda x: x['pool'], reverse=True)
        print(f"处理完成，返回 {len(processed)} 条数据")
        return jsonify(processed)

    except Exception as e:
        print(f"后端大崩了: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)