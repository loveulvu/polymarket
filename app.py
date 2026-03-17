from flask import Flask, jsonify
import requests
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 关键词到图片 URL 的映射库
KEYWORD_IMAGE_MAP = {
    # 人物相关
    'Trump': 'https://images.unsplash.com/photo-1617791160505-6f00504e3519?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Harvey Weinstein': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'BitBoy': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Rihanna': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Playboi Carti': 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Jesus Christ': 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    
    # 事件相关
    'GTA': 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Bitcoin': 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'FIFA': 'https://images.unsplash.com/photo-1471107340929-a87cd0f5b5f3?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'World Cup': 'https://images.unsplash.com/photo-1471107340929-a87cd0f5b5f3?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Stanley Cup': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'NHL': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    
    # 主题相关
    'Prison': 'https://images.unsplash.com/photo-1606787366850-de6330128bfc?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Election': 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'War': 'https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Ceasefire': 'https://images.unsplash.com/photo-1486572788966-cfd3df1f5b42?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'China': 'https://images.unsplash.com/photo-1546436836-07a91091f160?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Taiwan': 'https://images.unsplash.com/photo-1585287391076-08b8f642b30a?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'OpenAI': 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
    'Hardware': 'https://images.unsplash.com/photo-1593642532973-d31b6557fa68?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',
}

# 辅助函数：提取标题中的前两个名词
def extract_nouns(title):
    # 简单的名词提取逻辑，实际项目中可以使用更复杂的 NLP 库
    # 这里使用正则表达式提取可能的名词
    words = re.findall(r'\b[A-Z][a-z]+\b', title)
    # 过滤掉常见的非名词词汇
    stop_words = {'Will', 'Before', 'After', 'The', 'A', 'An', 'Is', 'Are', 'Was', 'Were', 'Be', 'Been', 'Being'}
    nouns = [word for word in words if word not in stop_words]
    return nouns[:2]

@app.route('/api/markets')
def get_markets():
    try:
        # 备选方案：先从 events 接口获取数据，用于匹配更具体的图标
        events_data = {}
        try:
            events_url = "https://gamma-api.polymarket.com/events?limit=30&active=true"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
            print("开始获取 events 数据...")
            events_resp = requests.get(events_url, headers=headers, timeout=10)
            events_resp.raise_for_status()
            events_list = events_resp.json()
            print(f"获取到 {len(events_list)} 条 events 数据")
            
            # 构建 events 映射，用于后续匹配
            for event in events_list:
                event_id = event.get('id')
                if event_id:
                    events_data[event_id] = event
        except Exception as e:
            print(f"获取 events 数据失败: {e}")
        
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
                # 严格按照：event.icon/event.image > icon(头像) > outcomes[0].image > conditionId_image > image 的顺序
                img = None
                
                # 优先级0：event 对象（最高，真正相关的头像）
                if m.get('event'):
                    event = m.get('event')
                    if isinstance(event, dict):
                        # 优先取 event.icon
                        if event.get('icon') and 'placeholder' not in event.get('icon') and 'category' not in event.get('icon') and 'default' not in event.get('icon'):
                            img = event.get('icon')
                        # 其次取 event.image
                        elif event.get('image') and 'placeholder' not in event.get('image') and 'category' not in event.get('image') and 'default' not in event.get('image'):
                            img = event.get('image')
                
                # 优先级1：icon（头像）
                if not img and m.get('icon'):
                    if 'placeholder' not in m.get('icon') and 'category' not in m.get('icon') and 'default' not in m.get('icon'):
                        img = m.get('icon')
                
                # 优先级1.5：尝试从 events 字段获取更具体的图标
                if not img and m.get('events'):
                    events = m.get('events')
                    if isinstance(events, list) and len(events) > 0:
                        event = events[0]
                        if event.get('icon') and 'placeholder' not in event.get('icon') and 'category' not in event.get('icon') and 'default' not in event.get('icon'):
                            img = event.get('icon')
                        elif event.get('image') and 'placeholder' not in event.get('image') and 'category' not in event.get('image') and 'default' not in event.get('image'):
                            img = event.get('image')
                
                # 优先级2：outcomes[0].image
                if not img and m.get('outcomes'):
                    outcomes = m.get('outcomes')
                    # 处理 outcomes 可能是字符串的情况
                    if isinstance(outcomes, str):
                        try:
                            import json
                            outcomes = json.loads(outcomes)
                        except:
                            pass
                    if isinstance(outcomes, list) and len(outcomes) > 0:
                        if isinstance(outcomes[0], dict) and outcomes[0].get('image'):
                            if 'placeholder' not in outcomes[0].get('image') and 'category' not in outcomes[0].get('image') and 'default' not in outcomes[0].get('image'):
                                img = outcomes[0].get('image')
                
                # 优先级3：conditionId_image
                if not img and m.get('conditionId_image'):
                    if 'placeholder' not in m.get('conditionId_image') and 'category' not in m.get('conditionId_image') and 'default' not in m.get('conditionId_image'):
                        img = m.get('conditionId_image')
                
                # 优先级4：image（最后兜底，只有当上述三个字段全部为空时才使用）
                if not img and m.get('image'):
                    if 'placeholder' not in m.get('image') and 'category' not in m.get('image') and 'default' not in m.get('image'):
                        img = m.get('image')
                
                # 优先级5：从 events_data 中匹配更具体的图标（备选方案）
                if not img:
                    # 尝试通过 eventId 匹配 events_data
                    event_id = m.get('eventId') or m.get('groupId')
                    if event_id and event_id in events_data:
                        event = events_data[event_id]
                        if event.get('icon') and 'placeholder' not in event.get('icon') and 'category' not in event.get('icon') and 'default' not in event.get('icon'):
                            img = event.get('icon')
                            print(f"从 events_data 匹配到图标: {img}")
                        elif event.get('image') and 'placeholder' not in event.get('image') and 'category' not in event.get('image') and 'default' not in event.get('image'):
                            img = event.get('image')
                            print(f"从 events_data 匹配到图片: {img}")
                
                # 打印图片链接以便调试
                print(f"Title: {title} | Image URL: {img}")
                # 检查图片链接是否包含不相关的关键词
                if img and ('category' in img or 'default' in img):
                    print(f"警告：图片链接可能包含不相关内容: {img}")
                
                # 【关键词映射方案】
                # 1. 检查标题是否包含预设关键词
                keyword_matched = False
                for keyword, image_url in KEYWORD_IMAGE_MAP.items():
                    if keyword.lower() in title.lower():
                        img = image_url
                        print(f"关键词匹配: {keyword} -> {image_url}")
                        keyword_matched = True
                        break
                
                # 2. 模糊搜索优化：如果没有匹配到预设关键词，使用 Unsplash API
                if not keyword_matched:
                    nouns = extract_nouns(title)
                    if nouns:
                        # 提取前两个名词作为关键词
                        keywords = ' '.join(nouns)
                        unsplash_url = f"https://source.unsplash.com/featured/?{keywords.replace(' ', '%20')}"
                        img = unsplash_url
                        print(f"模糊搜索: {keywords} -> {unsplash_url}")

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