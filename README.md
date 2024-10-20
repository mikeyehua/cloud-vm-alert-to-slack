
# 基于 Jupyter、Prometheus 和 Slack 的智能 IT 运维系统

本项目展示如何在服务器上使用开源工具构建**智能 IT 运维系统**。该系统从云主机（阿里云、腾讯云、Azure）收集指标数据，分析数据以检测异常，并在 CPU 使用率超过阈值时通过 Slack 自动发送告警。

---

## 架构概览

以下是系统流程的架构图，展示了 **Prometheus 监控**指标、**Jupyter Notebook 分析**数据、以及 **Slack 发送告警**的流程。

![架构图](architecture.png)

---

## 文件结构
```bash
├── cpu_monitor.py  # CPU 监控脚本
├── monitor.log     # 日志文件
```

---
## 组件

- **Linux 服务器**：承载所有服务的核心平台。
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

## 监控脚本

在项目目录下新建文件 **\`cpu_monitor.py\`**，并粘贴以下代码：

```python
import requests
import pandas as pd
import time

PROMETHEUS_URL = 'http://<你的Prometheus服务器>:9090/api/v1/query'
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/your/slack/webhook'
threshold = 80.0  # 告警阈值

def fetch_cpu_usage():
    query = '100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    response = requests.get(PROMETHEUS_URL, params={'query': query})
    data = response.json()['data']['result']
    return [{'instance': item['metric']['instance'], 'value': float(item['value'][1])} for item in data]

def send_alert(anomalies):
    message = f"⚠️ 警告！以下实例 CPU 使用率过高：
{pd.DataFrame(anomalies).to_string(index=False)}"
    requests.post(SLACK_WEBHOOK_URL, json={'text': message})

while True:
    metrics = fetch_cpu_usage()
    anomalies = [m for m in metrics if m['value'] > threshold]

    if anomalies:
        send_alert(anomalies)
        print("告警已发送到 Slack。")
    else:
        print("系统正常。")

    time.sleep(300)  # 每 5 分钟检查一次
```

---
## 运行监控程序

### 1. 使用 \`nohup\` 后台运行  
在终端中运行以下命令，确保监控程序在后台运行，并将输出保存到日志文件。

```bash
nohup python3 cpu_monitor.py > monitor.log 2>&1 &
```

- **\`nohup\`**：防止程序因会话断开而中止。  
- **\`&\`**：让程序在后台运行。  
- **\`monitor.log\`**：保存日志输出。

### 2. 检查进程是否运行  
```bash
ps aux | grep cpu_monitor.py
```

### 3. 停止后台进程  
找到进程号（PID）并终止进程：

```bash
kill <PID>
```

---

## 日志查看

查看监控程序的日志输出：

```bash
tail -f monitor.log
```

---
## 未来改进

- 集成 **Zammad** 实现基于告警的自动工单创建。
- 使用 **Grafana** 实现高级可视化与仪表盘。
- 探索 **scikit-learn** 等机器学习库，实现更复杂的异常检测模型。

---

## 许可证
本项目基于 MIT 许可证。
