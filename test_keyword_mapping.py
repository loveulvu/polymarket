import requests
import json

# 测试修改后的图片提取逻辑
def test_image_extraction():
    try:
        # 获取市场数据
        url = "http://localhost:5000/api/markets"
        
        print("开始测试 API 端点...")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        print(f"获取到 {len(data)} 条市场数据\n")
        
        # 分析返回的图片
        image_counts = {}
        for i, market in enumerate(data):
            title = market.get('title')
            image = market.get('image')
            
            if title and image:
                print(f"=== 第{i+1}条数据 ===")
                print(f"标题: {title}")
                print(f"图片: {image}")
                print()
                
                # 统计图片使用情况
                if image not in image_counts:
                    image_counts[image] = []
                image_counts[image].append(title)
        
        # 分析图片重复情况
        print("=== 图片重复分析 ===")
        for image, titles in image_counts.items():
            if len(titles) > 1:
                print(f"图片: {image}")
                print(f"使用次数: {len(titles)}")
                print("相关市场:")
                for title in titles[:3]:
                    print(f"  - {title}")
                if len(titles) > 3:
                    print(f"  ... 还有 {len(titles) - 3} 个市场")
                print()
        
        print("测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_extraction()
