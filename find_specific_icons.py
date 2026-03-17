import requests

# 查找可能包含具体图标的字段
try:
    url = "https://gamma-api.polymarket.com/markets?limit=3&active=true&closed=false"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    print("开始获取市场数据...")
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    print(f"获取到 {len(data)} 条市场数据\n")
    
    for i, m in enumerate(data):
        print(f"=== 第{i+1}条数据 ===")
        print(f"标题: {m.get('question') or m.get('description')}")
        
        # 查找可能包含具体图标的字段
        print(f"\n可能包含具体图标的字段:")
        print(f"  - icon: {m.get('icon')}")
        print(f"  - image: {m.get('image')}")
        print(f"  - conditionId_image: {m.get('conditionId_image')}")
        print(f"  - groupItemTitle: {m.get('groupItemTitle')}")
        print(f"  - slug: {m.get('slug')}")
        print(f"  - ticker: {m.get('ticker')}")
        
        # 检查 events 字段
        if m.get('events'):
            events = m.get('events')
            if isinstance(events, list) and len(events) > 0:
                event = events[0]
                print(f"\n  events[0] 的详细信息:")
                print(f"    - icon: {event.get('icon')}")
                print(f"    - image: {event.get('image')}")
                print(f"    - slug: {event.get('slug')}")
                print(f"    - ticker: {event.get('ticker')}")
        
        print("\n" + "="*50 + "\n")
        
except Exception as e:
    print(f"获取数据失败: {e}")
    import traceback
    traceback.print_exc()
