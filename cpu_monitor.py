import requests
import pandas as pd
import time

PROMETHEUS_URL = 'http://<你的Prometheus服务器>:9090/api/v1/query'
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/your/slack/webhook'
threshold = 80.0

def fetch_cpu_usage():
    query = '100 - (avg by(instance)(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    response = requests.get(PROMETHEUS_URL, params={'query': query})
    data = response.json()['data']['result']
    return [{'instance': item['metric']['instance'], 'value': float(item['value'][1])} for item in data]

def send_alert(anomalies):
    message = f"⚠️ 警告！以下实例 CPU 使用率过高：\n{pd.DataFrame(anomalies).to_string(index=False)}"
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
