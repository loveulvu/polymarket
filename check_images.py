import requests

# 测试 API 并查看图片链接
try:
    response = requests.get('http://127.0.0.1:5000/api/markets')
    data = response.json()
    
    print("前5条数据的图片链接:")
    for i, market in enumerate(data[:5]):
        print(f"\n第{i+1}条:")
        print(f"   标题: {market.get('title', 'N/A')}")
        print(f"   图片: {market.get('image', 'N/A')}")
        print(f"   YES 价格: {market.get('yes', 'N/A')}")
        
except Exception as e:
    print(f"测试 API 失败: {e}")
