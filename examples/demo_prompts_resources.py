#!/usr/bin/env python3
"""
Demo script to test MCP Prompts and Resources

This script demonstrates how to interact with your MCP server's
prompts and resources programmatically.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prometheus_mcp_server.simple_server import (
    prometheus,
    get_firing_alerts,
    get_metric,
    get_dashboard_overview,
    analyze_alert_prompt,
    performance_analysis_prompt,
)


async def demo_resources():
    """Demonstrate all MCP Resources"""
    print("=" * 80)
    print("🎯 DEMO: MCP RESOURCES (Live Data Sources)")
    print("=" * 80)
    print()
    
    # Resource 1: Firing Alerts
    print("📊 Resource 1: prometheus://alerts/firing")
    print("-" * 80)
    try:
        result = await get_firing_alerts()
        data = json.loads(result)
        print(f"✅ Success! Found {len(data.get('data', {}).get('result', []))} firing alerts")
        print(f"Preview: {json.dumps(data, indent=2)[:500]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Resource 2: Specific Metric
    print("📊 Resource 2: prometheus://metrics/{metric_name}")
    print("-" * 80)
    metric_name = "up"
    print(f"Testing with metric: '{metric_name}'")
    try:
        result = await get_metric(metric_name)
        data = json.loads(result)
        print(f"✅ Success! Got data for metric '{metric_name}'")
        print(f"Preview: {json.dumps(data, indent=2)[:500]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Resource 3: Dashboard Overview
    print("📊 Resource 3: prometheus://dashboard/overview")
    print("-" * 80)
    try:
        result = await get_dashboard_overview()
        data = json.loads(result)
        print(f"✅ Success! Dashboard overview retrieved")
        print("Metrics included:")
        for key in data.keys():
            status = "✅" if "error" not in str(data[key]) else "❌"
            print(f"  {status} {key}")
        print(f"\nPreview: {json.dumps(data, indent=2)[:500]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


async def demo_prompts():
    """Demonstrate all MCP Prompts"""
    print("=" * 80)
    print("🤖 DEMO: MCP PROMPTS (AI Analysis Templates)")
    print("=" * 80)
    print()
    
    # Prompt 1: Alert Analysis
    print("🔍 Prompt 1: analyze_alert_prompt")
    print("-" * 80)
    alert_name = "HighMemoryUsage"
    timerange = "2h"
    print(f"Parameters: alert_name='{alert_name}', timerange='{timerange}'")
    try:
        prompt_text = await analyze_alert_prompt(alert_name, timerange)
        print(f"✅ Success! Generated analysis prompt")
        print("\nPrompt Preview:")
        print("-" * 40)
        print(prompt_text[:600] + "...")
        print("-" * 40)
        print(f"\nPrompt length: {len(prompt_text)} characters")
        print("This prompt would be sent to the AI for analysis")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Prompt 2: Performance Analysis
    print("🔍 Prompt 2: performance_analysis_prompt")
    print("-" * 80)
    service = "api-service"
    duration = "24h"
    print(f"Parameters: service='{service}', duration='{duration}'")
    try:
        prompt_text = await performance_analysis_prompt(service, duration)
        print(f"✅ Success! Generated performance analysis prompt")
        print("\nPrompt Preview:")
        print("-" * 40)
        print(prompt_text[:600] + "...")
        print("-" * 40)
        print(f"\nPrompt length: {len(prompt_text)} characters")
        print("This prompt would be sent to the AI for analysis")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


async def demo_comparison():
    """Show the difference between Resources and Prompts"""
    print("=" * 80)
    print("🔬 COMPARISON: Resources vs Prompts")
    print("=" * 80)
    print()
    
    print("📊 RESOURCE Example (Raw Data):")
    print("-" * 80)
    try:
        resource_result = await get_firing_alerts()
        data = json.loads(resource_result)
        print("Returns: Raw JSON data from Prometheus")
        print(f"Type: {type(data)}")
        print(f"Keys: {list(data.keys())}")
        print("Use case: When you need the actual data")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    print("🤖 PROMPT Example (AI Instructions + Data):")
    print("-" * 80)
    try:
        prompt_result = await analyze_alert_prompt("TestAlert", "1h")
        print("Returns: Formatted prompt with data + analysis instructions")
        print(f"Type: {type(prompt_result)}")
        print(f"Length: {len(prompt_result)} characters")
        print("Use case: When you want AI to analyze the data")
        print("\nPrompt structure:")
        print("  1. Context (alert name, timerange)")
        print("  2. Data (fetched from Prometheus)")
        print("  3. Instructions (what to analyze)")
        print("  4. Expected output format")
    except Exception as e:
        print(f"Error: {e}")
    print()


async def interactive_demo():
    """Interactive demo menu"""
    print("\n" + "=" * 80)
    print("🎓 INTERACTIVE MCP DEMO")
    print("=" * 80)
    print()
    print("Choose a demo:")
    print("  1. Test all Resources (data sources)")
    print("  2. Test all Prompts (AI templates)")
    print("  3. Compare Resources vs Prompts")
    print("  4. Run all demos")
    print("  5. Exit")
    print()
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        await demo_resources()
    elif choice == "2":
        await demo_prompts()
    elif choice == "3":
        await demo_comparison()
    elif choice == "4":
        await demo_resources()
        await demo_prompts()
        await demo_comparison()
    elif choice == "5":
        print("Goodbye! 👋")
        return False
    else:
        print("Invalid choice!")
    
    return True


async def main():
    """Main demo runner"""
    print("\n" + "🚀 " * 20)
    print("MCP PROMPTS & RESOURCES DEMONSTRATION")
    print("🚀 " * 20)
    print()
    print("This demo will show you how your MCP server's prompts and resources work.")
    print()
    print(f"Prometheus URL: {prometheus.url}")
    print()
    
    # Check Prometheus connection
    print("Checking Prometheus connection...")
    try:
        health = await prometheus.health_check()
        if health.get("status") == "healthy":
            print("✅ Prometheus is healthy and reachable!")
        else:
            print("⚠️  Prometheus returned unhealthy status")
    except Exception as e:
        print(f"❌ Cannot connect to Prometheus: {e}")
        print("\nMake sure:")
        print("  1. Prometheus is running")
        print("  2. PROMETHEUS_URL is set correctly")
        print(f"     Current: {prometheus.url}")
        return
    
    print()
    
    # Run interactive demo
    while True:
        continue_demo = await interactive_demo()
        if not continue_demo:
            break
        
        print("\n" + "-" * 80)
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

