"""
SAP AI Core Deployment 并发测试脚本
测试单个 deployment 的并发处理能力
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List

@dataclass
class RequestResult:
    success: bool
    status_code: int
    latency_ms: float
    error: str = ""

def send_request(proxy_url: str, model: str, token: str, request_id: int) -> RequestResult:
    """发送单个请求并记录结果"""
    start = time.time()
    try:
        resp = requests.post(
            f"{proxy_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": f"Say 'test {request_id}' only"}],
                "max_tokens": 10
            },
            timeout=60
        )
        latency = (time.time() - start) * 1000
        
        if resp.status_code == 200:
            return RequestResult(True, resp.status_code, latency)
        else:
            return RequestResult(False, resp.status_code, latency, resp.text[:200])
    except Exception as e:
        latency = (time.time() - start) * 1000
        return RequestResult(False, 0, latency, str(e)[:200])

def run_concurrency_test(
    proxy_url: str,
    model: str, 
    token: str,
    concurrent_requests: int,
    total_requests: int
) -> List[RequestResult]:
    """运行并发测试"""
    results = []
    
    print(f"\n{'='*60}")
    print(f"并发测试: {model}")
    print(f"并发数: {concurrent_requests}, 总请求: {total_requests}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = {
            executor.submit(send_request, proxy_url, model, token, i): i 
            for i in range(total_requests)
        }
        
        for future in as_completed(futures):
            req_id = futures[future]
            result = future.result()
            results.append(result)
            
            status = "✓" if result.success else "✗"
            print(f"  [{status}] 请求 {req_id:3d}: {result.latency_ms:7.0f}ms - {result.status_code} {result.error[:50] if result.error else ''}")
    
    total_time = time.time() - start_time
    
    # 统计
    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count
    avg_latency = sum(r.latency_ms for r in results) / len(results) if results else 0
    success_latencies = [r.latency_ms for r in results if r.success]
    
    print(f"\n{'='*60}")
    print(f"测试结果:")
    print(f"  总请求:     {len(results)}")
    print(f"  成功:       {success_count} ({success_count/len(results)*100:.1f}%)")
    print(f"  失败:       {fail_count}")
    print(f"  总耗时:     {total_time:.2f}s")
    print(f"  平均延迟:   {avg_latency:.0f}ms")
    if success_latencies:
        print(f"  最快:       {min(success_latencies):.0f}ms")
        print(f"  最慢:       {max(success_latencies):.0f}ms")
    print(f"  吞吐量:     {len(results)/total_time:.2f} req/s")
    print(f"{'='*60}\n")
    
    return results

if __name__ == "__main__":
    # 配置
    PROXY_URL = "http://localhost:3001"
    TOKEN = "sap-ai-key"
    MODEL = "anthropic--claude-4.5-opus"  # 你有3个这个模型的deployment
    
    print("\n🚀 SAP AI Core 并发能力测试")
    print(f"   Proxy: {PROXY_URL}")
    print(f"   Model: {MODEL}")
    
    # 测试不同并发级别
    tests = [
        (1, 3),    # 1并发, 3请求 - 基准测试
        (3, 6),    # 3并发, 6请求 - 轻度并发
        (5, 10),   # 5并发, 10请求 - 中度并发
        # (10, 20),  # 10并发, 20请求 - 高并发 (可选，取消注释启用)
    ]
    
    for concurrent, total in tests:
        input(f"\n按 Enter 开始测试 (并发={concurrent}, 总数={total})...")
        run_concurrency_test(PROXY_URL, MODEL, TOKEN, concurrent, total)
    
    print("\n✅ 测试完成!")
