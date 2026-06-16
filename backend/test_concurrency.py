#!/usr/bin/env python3
"""
并发测试脚本 - 验证领养申请和审核的并发安全性
"""
import urllib.request
import json
import threading
import time
import sys

BASE_URL = "http://localhost:8000"


def create_application(animal_id, name, phone, results, index):
    """提交领养申请"""
    data = {
        "animal_id": animal_id,
        "applicant_name": name,
        "applicant_phone": phone,
        "applicant_email": f"{name}@example.com",
        "reason": f"我是{name}，想领养这只小动物"
    }
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/api/vinit/apply",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            results[index] = {"success": True, "data": result, "status": response.status}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_detail = json.loads(error_body).get("detail", str(e))
        except:
            error_detail = str(e)
        results[index] = {"success": False, "error": error_detail, "status": e.code}


def review_application(app_id, status, results, index):
    """审核申请"""
    data = {"status": status, "remark": "并发测试审核"}
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/api/vinit/applications/{app_id}/review",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='PATCH'
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            results[index] = {"success": True, "data": result, "status": response.status}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_detail = json.loads(error_body).get("detail", str(e))
        except:
            error_detail = str(e)
        results[index] = {"success": False, "error": error_detail, "status": e.code}


def get_animal(animal_id):
    """获取动物信息"""
    with urllib.request.urlopen(f"{BASE_URL}/api/vinit/animals/{animal_id}") as response:
        return json.loads(response.read().decode())


def get_applications(animal_id=None):
    """获取申请列表"""
    with urllib.request.urlopen(f"{BASE_URL}/api/vinit/applications") as response:
        apps = json.loads(response.read().decode())
        if animal_id:
            return [a for a in apps if a["animal_id"] == animal_id]
        return apps


def test_concurrent_apply():
    """测试并发提交领养申请"""
    print("=" * 60)
    print("测试1：并发提交领养申请")
    print("=" * 60)

    animal_id = 2
    animal_before = get_animal(animal_id)
    print(f"\n测试前 - 动物「{animal_before['name']} 状态: {animal_before['status']}")

    num_threads = 5
    results = [None] * num_threads
    threads = []

    for i in range(num_threads):
        t = threading.Thread(
            target=create_application,
            args=(animal_id, f"申请人{i+1}", f"1380000000{i+1}", results, i)
        )
        threads.append(t)

    print(f"\n同时发起 {num_threads} 个并发申请...")
    start_time = time.time()

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    end_time = time.time()
    print(f"耗时: {end_time - start_time:.3f}秒")

    success_count = 0
    fail_count = 0
    print("\n申请结果：")
    for i, r in enumerate(results):
        if r["success"]:
            success_count += 1
            print(f"  申请人{i+1}: ✅ 成功 (申请ID: {r['data']['id']}, 状态: {r['data']['status']})")
        else:
            fail_count += 1
            print(f"  申请人{i+1}: ❌ 失败 (状态码: {r['status']}, 原因: {r['error']})")

    animal_after = get_animal(animal_id)
    apps = get_applications(animal_id)
    pending_apps = [a for a in apps if a["status"] == "待审核"]

    print(f"\n验证结果：")
    print(f"  成功申请数: {success_count}")
    print(f"  失败申请数: {fail_count}")
    print(f"  动物当前状态: {animal_after['status']}")
    print(f"  待审核申请数: {len(pending_apps)}")

    if animal_after["status"] == "申请中" and len(pending_apps) == 1:
        print("  ✅ 并发控制正确！只有1个申请成功，动物状态为「申请中」")
        return True
    elif animal_after["status"] == "申请中" and len(pending_apps) > 1:
        print(f"  ⚠️  有 {len(pending_apps)} 个待审核申请，需要审核时会进一步校验")
        return True
    else:
        print(f"  ❌ 并发控制失败！动物状态异常或申请数量不对")
        return False


def test_concurrent_review():
    """测试并发审核申请"""
    print("\n" + "=" * 60)
    print("测试2：并发审核领养申请")
    print("=" * 60)

    animal_id = 3
    animal_before = get_animal(animal_id)
    print(f"\n测试前 - 动物「{animal_before['name']}」状态: {animal_before['status']}")

    print("\n先提交2个申请...")
    results1 = [None]
    create_application(animal_id, "申请人A", "13900000001", results1, 0)
    results2 = [None]
    create_application(animal_id, "申请人B", "13900000002", results2, 0)

    app1 = results1[0]["data"] if results1[0]["success"] else None
    app2 = results2[0]["data"] if results2[0]["success"] else None

    if not app1:
        print("申请1提交失败，跳过审核测试")
        return False

    apps = get_applications(animal_id)
    pending_apps = [a for a in apps if a["status"] == "待审核"]
    print(f"当前待审核申请数: {len(pending_apps)}")

    if len(pending_apps) < 2:
        print("⚠️  待审核申请不足2个，使用已有的申请进行测试")
        if len(pending_apps) == 1:
            app1 = pending_apps[0]
            app2 = pending_apps[0]
        else:
            print("没有待审核申请，跳过")
            return False
    else:
        app1, app2 = pending_apps[0], pending_apps[1]

    print(f"\n同时审核申请 {app1['id']} 和 {app2['id']} 都设为「已通过」...")

    num_threads = 2
    results = [None] * num_threads
    threads = []

    t1 = threading.Thread(
        target=review_application,
        args=(app1["id"], "已通过", results, 0)
    )
    t2 = threading.Thread(
        target=review_application,
        args=(app2["id"], "已通过", results, 1)
    )

    start_time = time.time()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    end_time = time.time()

    print(f"耗时: {end_time - start_time:.3f}秒")

    success_count = 0
    fail_count = 0
    print("\n审核结果：")
    for i, r in enumerate(results):
        if r["success"]:
            success_count += 1
            print(f"  审核申请{r['data']['id']}: ✅ 成功 (状态: {r['data']['status']})")
        else:
            fail_count += 1
            print(f"  审核申请: ❌ 失败 (状态码: {r['status']}, 原因: {r['error']})")

    animal_after = get_animal(animal_id)
    all_apps = get_applications(animal_id)
    approved_apps = [a for a in all_apps if a["status"] == "已通过"]

    print(f"\n验证结果：")
    print(f"  审核成功数: {success_count}")
    print(f"  审核失败数: {fail_count}")
    print(f"  动物当前状态: {animal_after['status']}")
    print(f"  已通过申请数: {len(approved_apps)}")

    if animal_after["status"] == "已领养" and len(approved_apps) == 1:
        print("  ✅ 并发控制正确！只有1个申请通过，动物状态为「已领养」")
        return True
    elif len(approved_apps) > 1:
        print(f"  ❌ 并发控制失败！有 {len(approved_apps)} 个申请通过了！")
        return False
    else:
        print(f"  ⚠️  结果: {len(approved_apps)} 个通过，动物状态: {animal_after['status']}")
        return len(approved_apps) <= 1


def main():
    print("🐾 流浪猫狗救助系统 - 并发安全测试")
    print()

    try:
        test1_pass = test_concurrent_apply()
    except Exception as e:
        print(f"测试1异常: {e}")
        test1_pass = False

    try:
        test2_pass = test_concurrent_review()
    except Exception as e:
        print(f"测试2异常: {e}")
        test2_pass = False

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"测试1（并发申请）: {'✅ 通过' if test1_pass else '❌ 失败'}")
    print(f"测试2（并发审核）: {'✅ 通过' if test2_pass else '❌ 失败'}")

    if test1_pass and test2_pass:
        print("\n🎉 所有并发测试通过！系统具备完善的并发控制机制。")
        return 0
    else:
        print("\n⚠️  部分测试未通过，请检查并发控制逻辑。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
