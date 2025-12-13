#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析所有测试结果并生成汇总报告
"""
import json
import glob
from datetime import datetime
from typing import Dict, List

def load_latest_results() -> Dict[str, dict]:
    """加载最新的测试结果"""
    results = {}
    
    # Test Set 1
    set1_files = glob.glob("test_results/test_set1_complete_*.json")
    if set1_files:
        latest_set1 = max(set1_files, key=lambda x: x.split('_')[-1])
        with open(latest_set1, 'r', encoding='utf-8') as f:
            results['set1'] = json.load(f)
    
    # Test Set 2
    set2_files = glob.glob("test_results/test_set2_complete_*.json")
    if set2_files:
        latest_set2 = max(set2_files, key=lambda x: x.split('_')[-1])
        with open(latest_set2, 'r', encoding='utf-8') as f:
            results['set2'] = json.load(f)
    
    # Test Set 3
    set3_files = glob.glob("test_results/test_set3_complete_*.json")
    if set3_files:
        latest_set3 = max(set3_files, key=lambda x: x.split('_')[-1])
        with open(latest_set3, 'r', encoding='utf-8') as f:
            results['set3'] = json.load(f)
    
    return results

def analyze_tool_routing(results: Dict[str, dict]) -> Dict:
    """分析工具路由准确性"""
    tool_stats = {
        'direct_llm': 0,
        'web_search': 0,
        'weather': 0,
        'local_rag': 0,
        'finance': 0,
        'transport': 0
    }
    
    # 问题案例
    issues = {
        'should_use_web_search': [],  # 应该用web_search但没用
        'wrong_tool': [],  # 工具选择错误
        'poor_answer': []  # 回答质量差
    }
    
    for set_name, data in results.items():
        if 'results' not in data:
            continue
            
        for item in data['results']:
            if not item['result']['success']:
                continue
                
            tools = item['result'].get('tools_used', [])
            answer = item['result'].get('answer', '')
            query = item['question']
            
            # 统计工具使用
            for tool in tools:
                if tool in tool_stats:
                    tool_stats[tool] += 1
            
            # 检测问题案例
            # 1. 天气查询（未来/其他城市）应该用web_search
            if any(kw in query.lower() for kw in ['tomorrow', '明天', 'shenzhen', '深圳']) and \
               any(kw in query.lower() for kw in ['weather', '天气', 'rain', '下雨']):
                if 'web_search' not in tools:
                    issues['should_use_web_search'].append({
                        'id': item['id'],
                        'query': query,
                        'tools': tools,
                        'answer': answer[:100]
                    })
            
            # 2. 实时信息查询（信号、开放状态等）应该用web_search
            if any(kw in query.lower() for kw in ['現在', '现在', 'now', '懸掛', '悬挂', 'signal', '信号']):
                if 'web_search' not in tools and 'direct_llm' in tools:
                    issues['should_use_web_search'].append({
                        'id': item['id'],
                        'query': query,
                        'tools': tools,
                        'answer': answer[:100]
                    })
            
            # 3. 回答质量检查
            if 'cannot answer' in answer.lower() or '无法回答' in answer or \
               'I cannot provide' in answer or 'I do not have' in answer:
                issues['poor_answer'].append({
                    'id': item['id'],
                    'query': query,
                    'tools': tools,
                    'answer': answer[:150]
                })
    
    return {
        'tool_usage': tool_stats,
        'issues': issues
    }

def generate_report(results: Dict[str, dict]):
    """生成汇总报告"""
    print("="*100)
    print("🧪 完整测试结果汇总报告")
    print("="*100)
    print(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 整体统计
    total_questions = 0
    total_successful = 0
    total_time = 0
    
    for set_name, data in results.items():
        if 'total_questions' in data:
            total_questions += data['total_questions']
            total_successful += data['successful']
            total_time += data.get('total_time_minutes', 0)
    
    print(f"📊 整体统计:")
    print(f"  总问题数: {total_questions}")
    print(f"  成功: {total_successful}/{total_questions} ({total_successful/total_questions*100:.1f}%)")
    print(f"  总耗时: {total_time:.1f}分钟")
    print()
    
    # 各测试集详细结果
    for set_name, data in results.items():
        print(f"📋 {set_name.upper()}:")
        print(f"  问题数: {data.get('total_questions', 0)}")
        print(f"  成功率: {data.get('success_rate', 0):.1f}%")
        print(f"  平均响应时间: {data.get('avg_response_time', 0):.2f}秒")
        print()
    
    # 工具路由分析
    analysis = analyze_tool_routing(results)
    print(f"🔧 工具使用统计:")
    for tool, count in sorted(analysis['tool_usage'].items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {tool}: {count}次")
    print()
    
    # 问题案例
    issues = analysis['issues']
    if issues['should_use_web_search']:
        print(f"⚠️  应该使用web_search但未使用的问题 ({len(issues['should_use_web_search'])}个):")
        for issue in issues['should_use_web_search'][:5]:  # 只显示前5个
            print(f"  [{issue['id']}] {issue['query'][:60]}...")
            print(f"    工具: {issue['tools']} | 回答: {issue['answer'][:80]}...")
        print()
    
    if issues['poor_answer']:
        print(f"⚠️  回答质量待改进的问题 ({len(issues['poor_answer'])}个):")
        for issue in issues['poor_answer'][:5]:
            print(f"  [{issue['id']}] {issue['query'][:60]}...")
            print(f"    工具: {issue['tools']} | 回答: {issue['answer']}")
        print()
    
    # 整体评价
    print("="*100)
    print("📈 整体评价:")
    
    success_rate = total_successful / total_questions * 100 if total_questions > 0 else 0
    avg_response = sum(data.get('avg_response_time', 0) for data in results.values()) / len(results) if results else 0
    
    if success_rate == 100:
        print("  ✅ 功能性: 完美 (100%成功率)")
    elif success_rate >= 95:
        print(f"  ✅ 功能性: 优秀 ({success_rate:.1f}%成功率)")
    else:
        print(f"  ⚠️  功能性: 良好 ({success_rate:.1f}%成功率，仍有提升空间)")
    
    if len(issues['should_use_web_search']) == 0:
        print("  ✅ 智能性: 优秀 (工具路由准确)")
    elif len(issues['should_use_web_search']) <= 5:
        print(f"  ⚠️  智能性: 良好 ({len(issues['should_use_web_search'])}个路由问题)")
    else:
        print(f"  ⚠️  智能性: 待改进 ({len(issues['should_use_web_search'])}个路由问题)")
    
    if avg_response < 15:
        print(f"  ✅ 性能: 优秀 (平均{avg_response:.1f}秒)")
    elif avg_response < 25:
        print(f"  ⚠️  性能: 良好 (平均{avg_response:.1f}秒)")
    else:
        print(f"  ⚠️  性能: 待优化 (平均{avg_response:.1f}秒)")
    
    print("="*100)

if __name__ == "__main__":
    results = load_latest_results()
    
    if not results:
        print("❌ 未找到测试结果文件")
    else:
        generate_report(results)

