import requests
import pandas as pd
from sklearn.cluster import KMeans
import time

PROMETHEUS_URL = 'http://<你的Prometheus服务器>:9090/api/v1/query'
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/your/slack/webhook'

# 获取 CPU 使用率数据
def fetch_cpu_usage():
    query = '100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    response = requests.get(PROMETHEUS_URL, params={'query': query})
    data = response.json()['data']['result']
    metrics = [{'instance': item['metric']['instance'], 'value': float(item['value'][1])} for item in data]
    return metrics

# 使用 K-means 进行异常检测
def detect_anomalies(data):
    df = pd.DataFrame(data)
    model = KMeans(n_clusters=2)  # 设置两类，正常和异常
    df['anomaly'] = model.fit_predict(df[['value']])
    
    # 返回异常实例
    anomalies = df[df['anomaly'] == 1]
    return anomalies

# 发送 Slack 告警
def send_alert(anomalies):
    message = f"⚠️ 警告！以下实例 CPU 使用率异常：\n{anomalies.to_string(index=False)}"
    requests.post(SLACK_WEBHOOK_URL, json={'text': message})

# 主程序
while True:
    cpu_metrics = fetch_cpu_usage()  # 获取 CPU 数据
    anomalies = detect_anomalies(cpu_metrics)  # 进行异常检测

    # 如果有异常则发送告警
    if not anomalies.empty:
        send_alert(anomalies)
        print("告警已发送到 Slack。")
    else:
        print("系统正常。")
    
    time.sleep(300)  # 每 5 分钟运行一次
