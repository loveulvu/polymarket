import requests
import json

# 详细分析数据结构，寻找具体图标
try:
    url = "https://gamma-api.polymarket.com/markets?limit=10&active=true&closed=false"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    print("开始获取市场数据...")
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    print(f"获取到 {len(data)} 条市场数据\n")
    
    for i, m in enumerate(data):
        title = m.get('question') or m.get('description')
        if not title: continue
        
        print(f"=== 第{i+1}条数据 ===")
        print(f"标题: {title}")
        print(f"\n当前使用的图标: {m.get('icon')}")
        print(f"通用背景图: {m.get('image')}")
        
        # 检查是否有其他可能的图标字段
        if m.get('groupItemTitle'):
            print(f"\n分组标题: {m.get('groupItemTitle')}")
        
        # 检查 outcomes 字段的详细结构
        if m.get('outcomes'):
            print(f"\noutcomes 类型: {type(m.get('outcomes'))}")
            print(f"outcomes 值: {m.get('outcomes')}")
        
        # 检查 events 字段
        if m.get('events'):
            print(f"\nevents 类型: {type(m.get('events'))}")
            if isinstance(m.get('events'), list) and len(m.get('events')) > 0:
                event = m.get('events')[0]
                print(f"event title: {event.get('title')}")
                print(f"event icon: {event.get('icon')}")
        
        # 检查是否有其他可能的图标相关字段
        print(f"\n其他可能的图标字段:")
        print(f"  - conditionId: {m.get('conditionId')}")
        print(f"  - slug: {m.get('slug')}")
        print(f"  - ticker: {m.get('ticker')}")
        print(f"  - groupItemId: {m.get('groupItemId')}")
        
        print("\n" + "="*60 + "\n")
        
except Exception as e:
    print(f"获取数据失败: {e}")
    import traceback
    traceback.print_exc()
