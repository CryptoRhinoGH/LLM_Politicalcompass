"""
runner.py

Automated experiment runner for evaluating political alignment and response behavior
of large language models (LLMs) under simulated user profiles.

This script:
- Iterates over combinations of cities, personas, and LLMs
- Spawns subprocesses to run `main.py` for each configuration
- Saves structured logs and results for each run in a timestamped output directory
- Retries failed runs once after all first-pass experiments complete

Command to run:
    caffeinate python us_healthcare_pipeline/runner.py

Dependencies:
- Assumes Python 3.8+ environment with necessary modules installed
- Assumes `main.py` is invokable as a module: `python -m us_healthcare_pipeline.main`
- Works best in a virtual environment with all `us_healthcare_pipeline` dependencies

Parameters:
- `cities` define locations used for proxy and search behavior
- `personas` define ideological browsing tendencies (e.g., left, right, neutral)
- `llms` specify the LLM to test (e.g., "chatgpt", "gemini")

Output:
- All results, logs, and metadata are stored under:
      us_healthcare_pipeline/results/<timestamp>/

Notes:
- The `caffeinate` wrapper on macOS prevents the system from sleeping during long runs
- Includes a 30-second delay between runs to reduce fingerprinting risk or browser reuse errors

Recommended Usage:
- Run in headful mode if debugging browser automation issues
- Review `log.txt` files in each run's folder to debug any subprocess failures
"""
import os
import sys
import time
import subprocess
from datetime import datetime

# ---- Experiment parameters ----
cities = ["Los Angeles", "Houston", "New York"]
personas = ["left", "right", "neutral"]
llms = ["chatgpt", "gemini"]  # Avoid "perplexity" if unstable

# ---- Output directory setup ----
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
base_results_dir = os.path.join("us_healthcare_pipeline", "results", timestamp)
os.makedirs(base_results_dir, exist_ok=True)

# ---- Track failed runs ----
failed_runs = []

def run_session(city, persona, llm, retry=False):
    run_name = f"{city.lower().replace(' ', '_')}_{persona}_{llm}"
    result_dir = os.path.join(base_results_dir, run_name)
    os.makedirs(result_dir, exist_ok=True)

    print(f"\n[{'RETRY' if retry else 'RUN'}] Starting: {city} | {persona} | {llm}")
    log_path = os.path.join(result_dir, "log.txt")
    print(f"[LOG] Output -> {log_path}")

    command = [
        sys.executable, "-m", "us_healthcare_pipeline.main",
        "--city", city,
        "--persona", persona,
        "--llm", llm,
        "--base_results_dir", result_dir
    ]

    try:
        with open(log_path, "w") as log_file:
            print(f"[SPAWN] Launching subprocess...")
            result = subprocess.run(command, stdout=log_file, stderr=log_file)

        if result.returncode != 0:
            print(f"[ERROR] Run failed: {city}, {persona}, {llm}")
            print(f"[NOTE] Check log file: {log_path}")
            if not retry:
                failed_runs.append((city, persona, llm))
        else:
            print(f"[DONE] Finished: {city}, {persona}, {llm}")
    except Exception as e:
        print(f"[EXCEPTION] {city}, {persona}, {llm}: {e}")
        if not retry:
            failed_runs.append((city, persona, llm))

    time.sleep(30)  # Throttle between runs


if __name__ == "__main__":
    print(f"[START] Experiment batch: {timestamp}")
    print(f"[DIR] Results saved to: {base_results_dir}")

    # Initial pass
    for city in cities:
        for persona in personas:
            for llm in llms:
                run_session(city, persona, llm)

    # Retry pass
    if failed_runs:
        print("\n[RETRY] Attempting failed runs again...")
        for city, persona, llm in failed_runs:
            run_session(city, persona, llm, retry=True)
    else:
        print("\n[INFO] No failed runs to retry.")

    print(f"\n[COMPLETE] All experiments finished.")