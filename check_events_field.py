import requests
import json

# 检查 events 字段的详细内容
def check_events_field():
    try:
        # 获取市场数据
        url = "https://gamma-api.polymarket.com/markets?limit=10&active=true&closed=false"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        print("开始获取市场数据...")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        print(f"获取到 {len(data)} 条市场数据\n")
        
        # 检查每个市场的 events 字段
        for i, m in enumerate(data):
            title = m.get('question') or m.get('description')
            if not title: continue
            
            print(f"=== 第{i+1}条数据 ===")
            print(f"标题: {title}")
            print(f"当前图片: {m.get('icon') or m.get('image')}")
            
            # 检查 events 字段
            if m.get('events'):
                events = m.get('events')
                print(f"events 类型: {type(events)}")
                if isinstance(events, list) and len(events) > 0:
                    for j, event in enumerate(events):
                        print(f"  event {j+1}:")
                        print(f"    id: {event.get('id')}")
                        print(f"    title: {event.get('title')}")
                        print(f"    icon: {event.get('icon')}")
                        print(f"    image: {event.get('image')}")
            
            # 检查是否有其他可能的图标字段
            print(f"其他可能的图标字段:")
            print(f"  - eventId: {m.get('eventId')}")
            print(f"  - groupId: {m.get('groupId')}")
            print(f"  - groupItemTitle: {m.get('groupItemTitle')}")
            
            print("\n" + "="*80 + "\n")
            
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_events_field()
