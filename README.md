
# 基于 Jupyter、Prometheus 和 Slack 的智能 IT 运维系统

本仓库展示如何在 RHEL 服务器上使用开源工具构建**智能 IT 运维系统**。该系统从云主机（阿里云、腾讯云、Azure）收集指标数据，分析数据以检测异常，并在 CPU 使用率超过阈值时通过 Slack 自动发送告警。

---

## 架构概览

以下是系统流程的架构图，展示了 **Prometheus 监控**指标、**Jupyter Notebook 分析**数据、以及 **Slack 发送告警**的流程。

![架构图](architecture.png)

---

## 组件

- **RHEL 服务器**：承载所有服务的核心平台。
- **Prometheus**：从云主机收集指标数据。
- **Jupyter Notebook**：分析指标并检测异常。
- **Slack**：发送检测到的异常告警。
- **Zammad**（可选）：可集成以管理工单。

---

## 安装与部署

### 1. 安装 Python 和 Jupyter Notebook
```bash
sudo dnf install python3 python3-pip -y
pip3 install notebook
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser
```

访问地址为：`http://<你的服务器IP>:8888`

### 2. 安装 Prometheus
下载并设置 Prometheus：
```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz
tar -xvzf prometheus-2.46.0.linux-amd64.tar.gz
cd prometheus-2.46.0.linux-amd64
./prometheus --config.file=prometheus.yml
```

### 3. 在 Jupyter Notebook 中查询指标数据
```python
import requests
import pandas as pd

PROMETHEUS_URL = 'http://<你的Prometheus服务器>:9090/api/v1/query'
query = '100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'

response = requests.get(PROMETHEUS_URL, params={'query': query})
data = response.json()['data']['result']

metrics = [{'instance': item['metric']['instance'], 'value': float(item['value'][1])} for item in data]
df = pd.DataFrame(metrics)
print(df)
```

### 4. 在 Jupyter Notebook 中可视化指标数据
```python
import matplotlib.pyplot as plt

df.plot(kind='bar', x='instance', y='value', legend=False)
plt.title('各实例 CPU 使用率')
plt.ylabel('CPU 使用率 (%)')
plt.xlabel('实例')
plt.show()
```

### 5. 异常检测与 Slack 告警
```python
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/your/slack/webhook'
threshold = 80.0
anomalies = df[df['value'] > threshold]

if not anomalies.empty:
    message = f"警告！检测到以下实例 CPU 使用率过高：
{anomalies.to_string(index=False)}"
    requests.post(SLACK_WEBHOOK_URL, json={'text': message})
    print("告警已发送到 Slack。")
else:
    print("未检测到异常。")
```

---

## 架构图

系统运行流程如下：

1. **Prometheus** 从阿里云、腾讯云和 Azure 主机收集指标。
2. **Jupyter Notebook** 从 Prometheus 获取指标并进行异常检测。
3. **Slack** 在检测到 CPU 使用率超过阈值时发送告警。

详细架构图如下：

![架构图](architecture.png)

---

## 未来改进

- 集成 **Zammad** 实现基于告警的自动工单创建。
- 使用 **Grafana** 实现高级可视化与仪表盘。
- 探索 **scikit-learn** 等机器学习库，实现更复杂的异常检测模型。

---

## 许可证
本项目基于 MIT 许可证。
