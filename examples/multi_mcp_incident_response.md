# Multi-MCP Incident Response Examples

This document shows real-world examples of using Prometheus MCP and Kubernetes MCP together for incident response.

## Example 1: Pod ImagePullBackOff Investigation

### Scenario
Alert firing: `RegistryAdapterPodNotRunning`

### Investigation Steps

**Step 1: Get the alert details (Prometheus MCP)**
```
User: "What alerts are currently firing?"

AI uses: alertmanager_get_alerts()

Result:
- Alert: RegistryAdapterPodNotRunning
- Pod: registry-adapter-7875bffcb4-kkxlw
- Namespace: registry-adapter-stubbed-showcase
- Severity: Minor
```

**Step 2: Check pod status with Prometheus metrics (Prometheus MCP)**
```
AI uses: prometheus_query('kube_pod_status_phase{pod="registry-adapter-7875bffcb4-kkxlw",namespace="registry-adapter-stubbed-showcase"}')

Result: Pod phase = Pending
```

**Step 3: Get detailed pod information (Kubernetes MCP)**
```
AI uses: k8s_get_pod(
    name="registry-adapter-7875bffcb4-kkxlw",
    namespace="registry-adapter-stubbed-showcase"
)

Result:
{
  "name": "registry-adapter-7875bffcb4-kkxlw",
  "namespace": "registry-adapter-stubbed-showcase",
  "phase": "Pending",
  "container_statuses": [{
    "name": "registry-adapter",
    "ready": false,
    "state": "waiting",
    "reason": "ImagePullBackOff",
    "message": "Back-off pulling image \"109614035486.dkr.ecr.eu-west-1.amazonaws.com/...\""
  }],
  "events": [
    {
      "type": "Warning",
      "reason": "Failed",
      "message": "Failed to pull image: rpc error: code = Unknown desc = Error response from daemon: pull access denied",
      "count": 15
    }
  ]
}
```

**Step 4: Get pod logs (Kubernetes MCP)**
```
AI uses: k8s_get_pod_logs(
    name="registry-adapter-7875bffcb4-kkxlw",
    namespace="registry-adapter-stubbed-showcase",
    tail_lines=50
)

Result: (No logs - container never started)
```

**Step 5: Check related services (Prometheus MCP)**
```
AI uses: prometheus_query('kube_deployment_status_replicas{deployment="ecr-proxy",namespace="registry-credentials-manager-int"}')

Result: ECR proxy deployment has 0 available replicas
```

**Step 6: Investigate ECR proxy (Kubernetes MCP)**
```
AI uses: k8s_get_deployment(
    name="ecr-proxy",
    namespace="registry-credentials-manager-int"
)

Result:
{
  "replicas": {
    "desired": 1,
    "current": 0,
    "ready": 0,
    "available": 0
  }
}
```

### Root Cause Analysis
```
AI Response:

Root Cause: ImagePullBackOff due to ECR authentication failure

Chain of failures:
1. ECR proxy deployment is down (0/1 replicas)
2. Without ECR proxy, pods cannot authenticate to ECR
3. registry-adapter pod cannot pull its image
4. Pod stuck in ImagePullBackOff

Recommendation:
1. Fix ECR proxy deployment first
2. Then the registry-adapter pod should recover automatically
```

---

## Example 2: ArgoCD Down - Complete Remediation

### Scenario
Multiple ArgoCD alerts firing, service is down.

### Full Workflow

**Step 1: Identify the problem (Prometheus MCP)**
```
User: "ArgoCD seems to be down, can you investigate?"

AI uses: alertmanager_get_alerts()

Result:
- 6 alerts: ArgocdApplicationNotRunning
- 5 alerts: ArgocdApplicationInsufficientReplicas
```

**Step 2: List ArgoCD pods (Kubernetes MCP)**
```
AI uses: k8s_list_pods(
    namespace="argocd",
    label_selector="app.kubernetes.io/name=argocd"
)

Result:
[
  {"name": "argocd-server-7986665999-8ms45", "phase": "CrashLoopBackOff", "ready": 0, "restarts": 15},
  {"name": "argocd-repo-server-85ccf774c9-6skk2", "phase": "CrashLoopBackOff", "ready": 0, "restarts": 12},
  {"name": "argocd-application-controller-0", "phase": "CrashLoopBackOff", "ready": 0, "restarts": 18}
]
```

**Step 3: Get details on one failing pod (Kubernetes MCP)**
```
AI uses: k8s_get_pod(
    name="argocd-server-7986665999-8ms45",
    namespace="argocd"
)

Result:
{
  "phase": "Running",
  "container_statuses": [{
    "state": "waiting",
    "reason": "CrashLoopBackOff"
  }],
  "events": [
    {"reason": "BackOff", "message": "Back-off restarting failed container"}
  ]
}
```

**Step 4: Get logs (Kubernetes MCP)**
```
AI uses: k8s_get_pod_logs(
    name="argocd-server-7986665999-8ms45",
    namespace="argocd",
    tail_lines=100
)

Result:
time="2024-12-05T10:00:00Z" level=fatal msg="Failed to connect to Redis: dial tcp 10.0.0.1:6379: connect: connection refused"
```

**Step 5: Check Redis (Prometheus MCP)**
```
AI uses: prometheus_query('up{job="redis",namespace="argocd"}')

Result: Redis is down (value = 0)
```

**Step 6: Check Redis deployment (Kubernetes MCP)**
```
AI uses: k8s_get_deployment(
    name="argocd-redis",
    namespace="argocd"
)

Result:
{
  "replicas": {
    "desired": 1,
    "current": 0,
    "ready": 0,
    "available": 0
  }
}
```

**Step 7: Get Redis pod status (Kubernetes MCP)**
```
AI uses: k8s_list_pods(
    namespace="argocd",
    label_selector="app=redis"
)

Result:
[
  {"name": "argocd-redis-74cb89f466-xyz", "phase": "Pending", "ready": 0}
]
```

**Step 8: Get Redis pod details (Kubernetes MCP)**
```
AI uses: k8s_get_pod(
    name="argocd-redis-74cb89f466-xyz",
    namespace="argocd"
)

Result:
{
  "events": [
    {
      "reason": "FailedScheduling",
      "message": "0/3 nodes are available: 3 Insufficient memory"
    }
  ]
}
```

**Step 9: Remediation - Scale down other services (if appropriate)**
```
User: "Can you restart Redis and see if that helps?"

AI uses: k8s_restart_deployment(
    name="argocd-redis",
    namespace="argocd"
)

Result: Deployment restarted
```

**Step 10: Monitor recovery (Kubernetes MCP)**
```
AI waits 30 seconds, then uses: k8s_list_pods(
    namespace="argocd",
    label_selector="app=redis"
)

Result:
[
  {"name": "argocd-redis-74cb89f466-abc", "phase": "Running", "ready": 1}
]
```

**Step 11: Verify ArgoCD pods recover (Kubernetes MCP)**
```
AI uses: k8s_list_pods(
    namespace="argocd",
    label_selector="app.kubernetes.io/name=argocd"
)

Result: All pods now Running with ready=1
```

**Step 12: Verify alerts cleared (Prometheus MCP)**
```
AI uses: alertmanager_get_alerts()

Result: ArgoCD alerts cleared!
```

### Summary
```
AI Response:

✅ Issue Resolved!

Root Cause:
- Redis pod failed to schedule due to insufficient memory on nodes
- ArgoCD components couldn't connect to Redis
- All ArgoCD pods were crashing

Remediation:
- Restarted Redis deployment
- New Redis pod scheduled successfully
- ArgoCD pods automatically recovered

Verification:
- All ArgoCD pods are now Running
- All alerts have cleared
- Services are healthy

Recommendation:
- Monitor cluster memory usage
- Consider adding more nodes or increasing node memory
- Review resource requests/limits for Redis
```

---

## Example 3: Deployment Scaling Based on Metrics

### Scenario
High CPU usage detected, need to scale deployment.

**Step 1: Check CPU metrics (Prometheus MCP)**
```
AI uses: prometheus_query('avg(rate(container_cpu_usage_seconds_total{pod=~"my-app.*"}[5m])) * 100')

Result: CPU usage = 85% (high!)
```

**Step 2: Get current deployment status (Kubernetes MCP)**
```
AI uses: k8s_get_deployment(
    name="my-app",
    namespace="production"
)

Result:
{
  "replicas": {
    "desired": 2,
    "current": 2,
    "ready": 2
  }
}
```

**Step 3: Scale up (Kubernetes MCP)**
```
User: "Please scale my-app to 4 replicas"

AI uses: k8s_scale_deployment(
    name="my-app",
    namespace="production",
    replicas=4
)

Result: Deployment scaled to 4 replicas
```

**Step 4: Monitor scaling (Kubernetes MCP)**
```
AI waits and uses: k8s_list_pods(
    namespace="production",
    label_selector="app=my-app"
)

Result: 4 pods, all Running
```

**Step 5: Verify CPU decreased (Prometheus MCP)**
```
AI uses: prometheus_query('avg(rate(container_cpu_usage_seconds_total{pod=~"my-app.*"}[5m])) * 100')

Result: CPU usage = 45% (improved!)
```

---

## Key Takeaways

### Why Multi-MCP is Powerful

1. **Complementary Data Sources**
   - Prometheus: Time-series metrics, trends, alerts
   - Kubernetes: Current state, events, logs

2. **Complete Investigation**
   - Prometheus tells you WHAT is wrong
   - Kubernetes tells you WHY it's wrong

3. **End-to-End Remediation**
   - Prometheus identifies the problem
   - Kubernetes fixes the problem
   - Prometheus verifies the fix

4. **Holistic View**
   - Metrics + Events + Logs + State
   - Past + Present
   - Monitoring + Orchestration

### Best Practices

1. **Always investigate before acting**
   - Use Kubernetes MCP to get full context
   - Check logs and events
   - Understand the root cause

2. **Use both perspectives**
   - Prometheus for trends and patterns
   - Kubernetes for point-in-time state

3. **Verify remediation**
   - Use Prometheus to confirm alerts cleared
   - Use Kubernetes to confirm pods are healthy

4. **Document your findings**
   - AI can generate incident reports
   - Combine data from both sources

