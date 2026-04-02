import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000/api"

def check_server():
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=3)
        if response.status_code == 200:
            return True
    except requests.exceptions.ConnectionError:
        pass
    return False

def print_metrics():
    try:
        response = requests.get(f"{BASE_URL}/metrics/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n----------------------------------------")
            print("SYSTEM METRICS")
            print("----------------------------------------")
            print(f"Queries Executed: {data.get('queries_executed', 0)}")
            
            if data.get('queries_executed', 0) > 0:
                print(f"P50 Latency:      {data.get('latency_p50', 0):.2f}s")
                print(f"Avg Similarity:   {data.get('avg_similarity', 0):.4f}")
                print(f"Avg Norm:         {data.get('avg_norm', 0):.4f}")
                
                alert_status = "YES" if data.get('drift_alert') else "NO"
                print(f"Drift Alert:      {alert_status}")
            print("----------------------------------------\n")
        else:
            print(f"\nFailed to fetch metrics. Status: {response.status_code}")
    except Exception as e:
        print(f"\nError fetching metrics: {e}")

def print_health():
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n----------------------------------------")
            print("SYSTEM HEALTH")
            print("----------------------------------------")
            
            print(f"Overall Status: {data.get('status', 'Unknown').upper()}")
            print(f"Database:       {data.get('postgres', 'Unknown').title()}")
            print("----------------------------------------\n")
        else:
            print(f"\nFailed to fetch health. Status: {response.status_code}")
    except Exception as e:
        print(f"\nError fetching health: {e}")

def run_chat():
    print("\n==================================================")
    print("RAG API Client Initializing...")
    
    if not check_server():
        print("ERROR: Could not connect to the Django server.")
        print("Please ensure python manage.py runserver is running.")
        return

    print("Connected to Server!")
    print("==================================================")
    print("Available Commands:")
    print("  /health  - Check system status")
    print("  /metrics - View query performance")
    print("  exit     - Quit the application")
    print("==================================================")

    while True:
        try:
            question = input("\nYou: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['exit', 'quit']:
                print("\nGoodbye!")
                break
                
            if question.lower() in ['/stats', '/metrics']:
                print_metrics()
                continue
                
            if question.lower() == '/health':
                print_health()
                continue

            print("Fetching from API...")
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/query/",
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=120.0 
            )
            
            if response.status_code == 200:
                data = response.json()
                req_time = time.time() - start_time
                print(f"Bot: {data.get('answer', 'No answer found.')}")
                print(f"   [Context Similarity: {data.get('similarity', 0):.4f} | Request Time: {req_time:.2f}s]")
            else:
                print(f"API Error ({response.status_code}): {response.text}")

        except requests.exceptions.Timeout:
            print("Request timed out. The LLM took too long to respond.")
        except KeyboardInterrupt:
            print("\n\nSession ended.")
            break
        except Exception as e:
            print(f"\nClient Error: {e}")

if __name__ == "__main__":
    run_chat()