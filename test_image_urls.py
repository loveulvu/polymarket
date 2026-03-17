import requests

# 测试图片URL是否有效
def test_image_urls():
    urls = [
        'https://images.unsplash.com/photo-1617791160505-6f00504e3519?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',  # Trump
        'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',  # Harvey Weinstein
        'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',  # BitBoy
        'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',  # Rihanna
        'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',  # Playboi Carti
        'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',  # GTA, Bitcoin
        'https://images.unsplash.com/photo-1471107340929-a87cd0f5b5f3?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',  # FIFA, World Cup
        'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3',  # Stanley Cup, NHL
        'https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3'  # OpenAI, Hardware
    ]
    
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            print(f"{url}: {r.status_code}")
        except Exception as e:
            print(f"{url}: {e}")

if __name__ == "__main__":
    test_image_urls()
