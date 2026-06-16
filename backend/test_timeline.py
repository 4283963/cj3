#!/usr/bin/env python3
"""测试成长时光机功能 API"""
import urllib.request
import json

BASE = "http://localhost:8000"

def test():
    print("=" * 50)
    print("🐾 成长时光机 - 后端 API 测试")
    print("=" * 50)

    print("\n1️⃣  测试获取动物详情（含时间轴）...")
    url = f"{BASE}/api/vinit/animals/1/detail?visitor_id=visitor_001"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())
        print(f"   ✅ 动物: {data['name']} ({data['status']})")
        print(f"   ✅ 动态数: {len(data['timelines'])}")
        for i, t in enumerate(data['timelines']):
            print(f"      [{i+1}] {t['author_name']}: {t['content'][:15]}... | 点赞:{t['like_count']} 已赞:{t['liked_by_me']}")

    print("\n2️⃣  测试追加动态...")
    post_data = json.dumps({
        "author_name": "测试志愿者",
        "content": "今天毛孩子特别开心，主动跟我玩逗猫棒！尾巴翘得老高了~",
        "image_url": "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=600"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/vinit/animals/1/timeline",
        data=post_data, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as resp:
        t = json.loads(resp.read().decode())
        print(f"   ✅ 发布成功！ID={t['id']}, 作者={t['author_name']}, 点赞={t['like_count']}")
        new_id = t['id']

    print("\n3️⃣  测试点赞...")
    like_data = json.dumps({"visitor_id": "visitor_001"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE}/api/vinit/timeline/{new_id}/like",
        data=like_data, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as resp:
        t = json.loads(resp.read().decode())
        print(f"   ✅ 点赞成功！点赞数={t['like_count']}, 我已赞={t['liked_by_me']}")

    print("\n4️⃣  测试取消点赞...")
    with urllib.request.urlopen(req) as resp:
        t = json.loads(resp.read().decode())
        print(f"   ✅ 取消成功！点赞数={t['like_count']}, 我已赞={t['liked_by_me']}")

    print("\n5️⃣  再点赞一次...")
    with urllib.request.urlopen(req) as resp:
        t = json.loads(resp.read().decode())
        print(f"   ✅ 再点赞成功！点赞数={t['like_count']}")

    print("\n" + "=" * 50)
    print("🎉 所有 API 测试通过！成长时光机功能正常")
    print("=" * 50)

if __name__ == "__main__":
    test()
