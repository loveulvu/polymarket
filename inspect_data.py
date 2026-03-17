import requests
import json

# 详细查看数据结构，寻找具体的图标
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
        print(f"\n所有字段:")
        for key, value in m.items():
            if key not in ['question', 'description']:
                print(f"  {key}: {value}")
        
        print(f"\n详细查看 outcomes:")
        if m.get('outcomes'):
            for j, outcome in enumerate(m.get('outcomes')):
                print(f"  Outcome {j}: {outcome}")
        
        print("\n" + "="*50 + "\n")
        
except Exception as e:
    print(f"获取数据失败: {e}")
    import traceback
    traceback.print_exc()
