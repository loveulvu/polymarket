import requests
import json

# 测试新的图片提取逻辑
try:
    url = "https://gamma-api.polymarket.com/markets?limit=5&active=true&closed=false"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    print("开始获取市场数据...")
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    print(f"获取到 {len(data)} 条市场数据\n")
    
    for i, m in enumerate(data):
        # 1. 提取标题
        title = m.get('question') or m.get('description')
        if not title: continue

        # 2. 【死磕图片相关性】
        # 严格按照：icon(头像) > events[0].icon > outcomes[0].image > conditionId_image > image 的顺序
        img = None
        
        # 优先级1：icon（最高）
        if m.get('icon') and 'placeholder' not in m.get('icon'):
            img = m.get('icon')
            print(f"使用优先级1 (icon): {img}")
        
        # 优先级1.5：尝试从 events 字段获取更具体的图标
        if not img and m.get('events'):
            events = m.get('events')
            if isinstance(events, list) and len(events) > 0:
                event = events[0]
                if event.get('icon') and 'placeholder' not in event.get('icon'):
                    img = event.get('icon')
                    print(f"使用优先级1.5 (events[0].icon): {img}")
        
        # 优先级2：outcomes[0].image
        if not img and m.get('outcomes'):
            outcomes = m.get('outcomes')
            # 处理 outcomes 可能是字符串的情况
            if isinstance(outcomes, str):
                try:
                    outcomes = json.loads(outcomes)
                except:
                    pass
            if isinstance(outcomes, list) and len(outcomes) > 0:
                if isinstance(outcomes[0], dict) and outcomes[0].get('image'):
                    img = outcomes[0].get('image')
                    print(f"使用优先级2 (outcomes[0].image): {img}")
        
        # 优先级3：conditionId_image
        if not img and m.get('conditionId_image'):
            img = m.get('conditionId_image')
            print(f"使用优先级3 (conditionId_image): {img}")
        
        # 优先级4：image（最后兜底，只有当上述三个字段全部为空时才使用）
        if not img and m.get('image'):
            img = m.get('image')
            print(f"使用优先级4 (image): {img}")
        
        # 打印图片链接以便调试
        print(f"Title: {title} | Image URL: {img}")
        print(f"原始数据中的字段:")
        print(f"  - icon: {m.get('icon')}")
        print(f"  - events: {m.get('events')}")
        print(f"  - outcomes: {m.get('outcomes')}")
        print(f"  - conditionId_image: {m.get('conditionId_image')}")
        print(f"  - image: {m.get('image')}")
        print()
        
except Exception as e:
    print(f"获取数据失败: {e}")
    import traceback
    traceback.print_exc()
