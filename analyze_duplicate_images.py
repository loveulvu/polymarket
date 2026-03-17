import requests
import json

# 分析重复图片的市场数据
def analyze_duplicate_images():
    try:
        # 获取市场数据
        url = "https://gamma-api.polymarket.com/markets?limit=50&active=true&closed=false"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        print("开始获取市场数据...")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        print(f"获取到 {len(data)} 条市场数据\n")
        
        # 按图片分组
        image_groups = {}
        for m in data:
            title = m.get('question') or m.get('description')
            if not title: continue
            
            # 提取图片
            img = None
            if m.get('icon'):
                img = m.get('icon')
            elif m.get('image'):
                img = m.get('image')
            
            if img:
                if img not in image_groups:
                    image_groups[img] = []
                image_groups[img].append(title)
        
        # 分析重复图片的组
        print("=== 重复图片分析 ===")
        for img, titles in image_groups.items():
            if len(titles) > 1:
                print(f"\n图片: {img}")
                print(f"使用该图片的市场数量: {len(titles)}")
                print("市场标题:")
                for title in titles[:5]:  # 只显示前5个
                    print(f"  - {title}")
                if len(titles) > 5:
                    print(f"  ... 还有 {len(titles) - 5} 个市场")
        
        # 检查是否有其他可能的图标字段
        print("\n=== 检查其他可能的图标字段 ===")
        if data:
            sample = data[0]
            print("示例市场的所有字段:")
            for key, value in sample.items():
                if isinstance(value, (str, int, float, bool)) and len(str(value)) < 100:
                    print(f"  {key}: {value}")
                elif isinstance(value, list) and len(value) > 0:
                    print(f"  {key}: [列表，长度: {len(value)}]")
                elif isinstance(value, dict):
                    print(f"  {key}: [字典，键: {list(value.keys())[:5]}]")
        
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_duplicate_images()
