#!/usr/bin/env python3
"""
Google Custom Search API权限检查脚本
检查API Key权限、CSE ID有效性等
"""
import sys
from pathlib import Path
import requests

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.core.config import settings


def check_api_key_permissions():
    """检查API Key权限"""
    print("=" * 80)
    print("Google Custom Search API 权限检查")
    print("=" * 80)
    
    api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', None)
    cse_id = getattr(settings, 'GOOGLE_CSE_ID', None)
    
    print(f"\n📋 当前配置:")
    print(f"  API Key: {api_key[:20]}..." if api_key else "  API Key: 未配置")
    print(f"  CSE ID: {cse_id if cse_id else '未配置'}")
    
    if not api_key or not cse_id:
        print("\n❌ 错误: API Key或CSE ID未配置")
        return
    
    print(f"\n🔍 测试API调用...")
    print("-" * 80)
    
    # 测试1: 简单搜索查询
    test_query = "Python"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": test_query,
        "num": 1
    }
    
    try:
        print(f"  测试查询: '{test_query}'")
        response = requests.get(url, params=params, timeout=10)
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_results = data.get("searchInformation", {}).get("totalResults", 0)
            print(f"  ✅ API调用成功！")
            print(f"  📊 找到 {total_results} 个结果")
            
            items = data.get("items", [])
            if items:
                print(f"\n  示例结果:")
                for i, item in enumerate(items[:2], 1):
                    print(f"    {i}. {item.get('title', 'N/A')}")
                    print(f"       {item.get('snippet', 'N/A')[:80]}...")
            
            return True
            
        elif response.status_code == 400:
            print(f"  ❌ 400 Bad Request")
            try:
                error_data = response.json()
                error_message = error_data.get("error", {})
                error_reason = error_message.get("message", "未知错误")
                print(f"  📝 错误信息: {error_reason}")
                
                # 常见错误分析
                if "Invalid API key" in error_reason or "API key not valid" in error_reason:
                    print(f"\n  💡 解决方案:")
                    print(f"     1. 检查API Key是否正确")
                    print(f"     2. 确认API Key已启用'Custom Search API'")
                    print(f"     3. 访问: https://console.cloud.google.com/apis/credentials")
                    print(f"     4. 找到你的API Key，点击'编辑'")
                    print(f"     5. 在'API限制'中确保已启用'Custom Search API'")
                    
                elif "Invalid cx" in error_reason or "invalid CSE ID" in error_reason:
                    print(f"\n  💡 解决方案:")
                    print(f"     1. 检查CSE ID是否正确")
                    print(f"     2. 访问: https://programmablesearchengine.google.com/controlpanel/all")
                    print(f"     3. 确认CSE ID存在且已激活")
                    print(f"     4. 确认搜索范围配置正确（如果要搜索整个网络，需要配置为'整个网络'）")
                    
                elif "Daily Limit Exceeded" in error_reason or "quota" in error_reason.lower():
                    print(f"\n  💡 解决方案:")
                    print(f"     1. 免费配额：每天100次搜索")
                    print(f"     2. 如果配额已用完，需要等待重置（每天UTC 0:00）")
                    print(f"     3. 或升级到付费计划")
                    
            except:
                print(f"  📝 原始响应: {response.text[:200]}")
                
        elif response.status_code == 403:
            print(f"  ❌ 403 Forbidden")
            try:
                error_data = response.json()
                error_message = error_data.get("error", {})
                error_reason = error_message.get("message", "未知错误")
                print(f"  📝 错误信息: {error_reason}")
                
                if "API key not valid" in error_reason:
                    print(f"\n  💡 解决方案:")
                    print(f"     1. API Key无效或未启用Custom Search API")
                    print(f"     2. 访问: https://console.cloud.google.com/apis/library/customsearch.googleapis.com")
                    print(f"     3. 点击'启用'以启用Custom Search API")
                    print(f"     4. 然后检查API Key权限")
                    
            except:
                print(f"  📝 原始响应: {response.text[:200]}")
                
        elif response.status_code == 401:
            print(f"  ❌ 401 Unauthorized")
            print(f"  📝 API Key认证失败")
            print(f"\n  💡 解决方案:")
            print(f"     1. 检查API Key是否正确")
            print(f"     2. 确认API Key已启用并配置了正确的权限")
            
        else:
            print(f"  ❌ HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"  📝 错误详情: {error_data}")
            except:
                print(f"  📝 原始响应: {response.text[:200]}")
                
    except requests.exceptions.Timeout:
        print(f"  ❌ 请求超时")
        print(f"  💡 检查网络连接或稍后重试")
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 请求失败: {e}")
        
    except Exception as e:
        print(f"  ❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
    
    return False


def check_api_key_details():
    """提供详细的API Key配置步骤"""
    print(f"\n\n📖 API Key配置步骤:")
    print("=" * 80)
    print("""
1. 访问Google Cloud Console:
   https://console.cloud.google.com/apis/credentials

2. 找到你的API Key (247520e58efa7b02a382...)

3. 点击"编辑"按钮

4. 在"API限制"部分:
   - 选择"限制密钥"
   - 在"选择要限制的API"中搜索"Custom Search API"
   - 确保已勾选"Custom Search API"

5. 如果没有看到Custom Search API，需要先启用它:
   - 访问: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
   - 点击"启用"按钮

6. 保存更改并等待几分钟让更改生效

7. 重新运行此脚本测试
""")


if __name__ == "__main__":
    success = check_api_key_permissions()
    
    if not success:
        check_api_key_details()
    
    print(f"\n{'=' * 80}")
    print("检查完成！")

