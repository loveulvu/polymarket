import requests
import json

# 测试图片提取逻辑
def test_image_extraction():
    try:
        # 先从 events 接口获取数据
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
            
            # 构建 events 映射
            for event in events_list:
                event_id = event.get('id')
                if event_id:
                    events_data[event_id] = event
        except Exception as e:
            print(f"获取 events 数据失败: {e}")
        
        # 获取市场数据
        url = "https://gamma-api.polymarket.com/markets?limit=10&active=true&closed=false"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        print("\n开始获取市场数据...")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        print(f"获取到 {len(data)} 条市场数据\n")
        
        # 测试图片提取逻辑
        for i, m in enumerate(data):
            try:
                # 1. 提取标题
                title = m.get('question') or m.get('description')
                if not title: continue
                
                print(f"=== 第{i+1}条数据 ===")
                print(f"标题: {title}")
                
                # 2. 图片提取逻辑
                img = None
                
                # 优先级0：event 对象（最高，真正相关的头像）
                if m.get('event'):
                    event = m.get('event')
                    if isinstance(event, dict):
                        # 优先取 event.icon
                        if event.get('icon') and 'placeholder' not in event.get('icon') and 'category' not in event.get('icon') and 'default' not in event.get('icon'):
                            img = event.get('icon')
                            print(f"使用优先级0 (event.icon): {img}")
                        # 其次取 event.image
                        elif event.get('image') and 'placeholder' not in event.get('image') and 'category' not in event.get('image') and 'default' not in event.get('image'):
                            img = event.get('image')
                            print(f"使用优先级0 (event.image): {img}")
                
                # 优先级1：icon（头像）
                if not img and m.get('icon'):
                    if 'placeholder' not in m.get('icon') and 'category' not in m.get('icon') and 'default' not in m.get('icon'):
                        img = m.get('icon')
                        print(f"使用优先级1 (icon): {img}")
                
                # 优先级1.5：尝试从 events 字段获取更具体的图标
                if not img and m.get('events'):
                    events = m.get('events')
                    if isinstance(events, list) and len(events) > 0:
                        event = events[0]
                        if event.get('icon') and 'placeholder' not in event.get('icon') and 'category' not in event.get('icon') and 'default' not in event.get('icon'):
                            img = event.get('icon')
                            print(f"使用优先级1.5 (events[0].icon): {img}")
                        elif event.get('image') and 'placeholder' not in event.get('image') and 'category' not in event.get('image') and 'default' not in event.get('image'):
                            img = event.get('image')
                            print(f"使用优先级1.5 (events[0].image): {img}")
                
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
                            if 'placeholder' not in outcomes[0].get('image') and 'category' not in outcomes[0].get('image') and 'default' not in outcomes[0].get('image'):
                                img = outcomes[0].get('image')
                                print(f"使用优先级2 (outcomes[0].image): {img}")
                
                # 优先级3：conditionId_image
                if not img and m.get('conditionId_image'):
                    if 'placeholder' not in m.get('conditionId_image') and 'category' not in m.get('conditionId_image') and 'default' not in m.get('conditionId_image'):
                        img = m.get('conditionId_image')
                        print(f"使用优先级3 (conditionId_image): {img}")
                
                # 优先级4：image（最后兜底）
                if not img and m.get('image'):
                    if 'placeholder' not in m.get('image') and 'category' not in m.get('image') and 'default' not in m.get('image'):
                        img = m.get('image')
                        print(f"使用优先级4 (image): {img}")
                
                # 优先级5：从 events_data 中匹配更具体的图标（备选方案）
                if not img:
                    # 尝试通过 eventId 匹配 events_data
                    event_id = m.get('eventId') or m.get('groupId')
                    if event_id and event_id in events_data:
                        event = events_data[event_id]
                        if event.get('icon') and 'placeholder' not in event.get('icon') and 'category' not in event.get('icon') and 'default' not in event.get('icon'):
                            img = event.get('icon')
                            print(f"使用优先级5 (events_data.icon): {img}")
                        elif event.get('image') and 'placeholder' not in event.get('image') and 'category' not in event.get('image') and 'default' not in event.get('image'):
                            img = event.get('image')
                            print(f"使用优先级5 (events_data.image): {img}")
                
                # 打印最终结果
                print(f"最终选定的图片: {img}")
                # 检查图片链接是否包含不相关的关键词
                if img and ('category' in img or 'default' in img):
                    print(f"警告：图片链接可能包含不相关内容: {img}")
                
                print("\n" + "="*80 + "\n")
                
            except Exception as e:
                print(f"处理数据失败: {e}")
                import traceback
                traceback.print_exc()
                print("\n" + "="*80 + "\n")
                continue
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_extraction()
