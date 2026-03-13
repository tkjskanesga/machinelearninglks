import os
import json
import boto3
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT") # Ollama API Endpoint
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", 'qwen2.5:1.5b') # Ollama Model
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN") # Sending Mail Message
LOG_GROUP_NAME = os.getenv("LOG_GROUP_NAME") # Deprecated (No More Use Again)
LIST_SNS_TOPIC_ARN = os.getenv("LIST_SNS_TOPIC_ARN") # Format '{"AlarmCrash":"arn:aws:sns:region:yyyy:xxxx",...othr}'
AWS_REGION = os.getenv("AWS_REGION", 'us-east-1') # Default vriginia

print("--- Checking Environment ---")
print(f"Ollama API: {OLLAMA_ENDPOINT}")
print(f"Ollama Model: {OLLAMA_MODEL}")
print(f"SNS Topic ARN: {SNS_TOPIC_ARN}")
print(f"List SNS Topic ARN: {LIST_SNS_TOPIC_ARN}")
print(f"AWS Region: {AWS_REGION}")
print("--- End Checking Environment ---")

client_logs = boto3.client('logs', region_name=AWS_REGION)
client_sns = boto3.client('sns', region_name=AWS_REGION)

def process_and_analyze(alarm_name):
  print(f"Trigger Alarm: {alarm_name}")
  try:
    mapping = {}
    if LIST_SNS_TOPIC_ARN:
      try:
        mapping = json.loads(LIST_SNS_TOPIC_ARN)
      except json.JSONDecodeError:
        pass
        
    import time
    log_res = {'events': []}
    if alarm_name in mapping:
      log_group_name = mapping[alarm_name]
      if not log_group_name:
        print("ga ada target log management yang ditemuin")
      else:
        start_time = int((time.time() - 3600) * 1000) # 1 hour ago
        log_res = client_logs.filter_log_events(
          logGroupName=log_group_name,
          filterPattern='ERROR',
          limit=5,
          startTime=start_time
        )
    
    _all_events = log_res.get('events', [])
    if not isinstance(_all_events, list):
      _all_events = []
    start_idx = max(0, len(_all_events) - 2)

    recent_events = [_all_events[i] for i in range(start_idx, len(_all_events))]
    logs = "\n".join([e['message'] for e in recent_events])
    if not logs:
      logs = "__Tidak ada log error spesifik ditemukan di CloudWatch Logs.__"

    print(f"Log {logs}")
    prompt = (
      "Sebagai DevOps, berikan 1 ringkasan penyebab error (Summary Masalah) dan 1 rekomendasi (Solusi Masalah) secara keseluruhan dari semua log berikut. "
      "JANGAN membahas log-nya satu per satu. Jadikan satu kesimpulan saja.\n\n"
      "ATURAN FORMAT (Gunakan teks polos tanpa markdown):\n"
      "🪄 Summary Masalah\n"
      "[Tulis satu paragraf ringkasan penyebab masalah di sini]\n\n"
      "🔧 Solusi Masalah\n"
      "[Tulis solusi teknis di sini]\n\n"
      f"Log Error:\n{logs}\n\n"
      "Jawaban sesuai template:"
    )

    ollama_payload = {
      "model": OLLAMA_MODEL,
      "prompt": prompt,
      "stream": False,
      "temperature": 0.6,
      "max_tokens": 2048,
    }

    response = requests.post(OLLAMA_ENDPOINT, json=ollama_payload)
    print(response.json())

    if response.json().get('error'):
      print(f"Error: {response.json().get('error')}")
      # Break
      return
    
    ai_text = response.json().get('response', 'Gagal memproses analisa dari Ollama.')

    client_sns.publish(
      TopicArn=SNS_TOPIC_ARN,
      Subject=f"Resume Incident Report: {alarm_name}",
      Message=f"📦 Error Log\n\n{logs}\n\n{ai_text}"
    )
    print(f"Berhasil mengirim analisa menggunakan model {OLLAMA_MODEL} ke SNS.")

  except Exception as e:
    print(f"Terjadi kesalahan: {str(e)}")

@app.post("/webhook")
async def handle_sns_webhook(request: Request, background_tasks: BackgroundTasks):
  body = await request.body()
  if not body:
    return {"error": "Empty body"}

  try:
    data = json.loads(body)
  except json.JSONDecodeError:
    return {"error": "Invalid JSON"}

  if data.get("Type") == "SubscriptionConfirmation":
    subscribe_url = data.get("SubscribeURL")
    requests.get(subscribe_url)
    return {"status": "Subscription confirmed"}

  if data.get("Type") == "Notification":
    raw_message = data.get("Message")
    alarm_name = "DefaultAlarm"
    if isinstance(raw_message, str):
      try:
        msg_payload = json.loads(raw_message)
        if isinstance(msg_payload, dict):
          alarm_name = msg_payload.get("AlarmName", alarm_name)
      except json.JSONDecodeError:
        pass
    elif isinstance(raw_message, dict):
      alarm_name = raw_message.get("AlarmName", alarm_name)

    background_tasks.add_task(process_and_analyze, alarm_name)

  return {"status": "ok"}

if __name__ == "__main__":
  import uvicorn
  server_port = int(os.getenv("PORT", 8080))
  uvicorn.run(app, host="0.0.0.0", port=server_port)