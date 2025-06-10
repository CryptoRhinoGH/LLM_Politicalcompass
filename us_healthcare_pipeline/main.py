"""
main.py

This script runs a complete simulated user session for evaluating political alignment
and response behavior of large language models (LLMs) using a specified persona and city.

Functionality:
- Loads a city-specific proxy and a persona's search/news behavior profile
- Launches a browser session with fingerprinted browsing and proxy configuration
- Simulates browsing behavior according to the persona's preferences
- Queries an LLM (e.g., ChatGPT or Gemini) with a fixed set of healthcare-related questions
- Saves metadata, browsing history, and model responses to structured output files

Usage:
python -m us_healthcare_pipeline.main --city "New York" --persona left --llm gemini
"""
import argparse
import os
from datetime import datetime

from us_healthcare_pipeline.services.session_manager import SessionManager
from us_healthcare_pipeline.services.llms.chatgpt_interface import ChatGPTInterface
from us_healthcare_pipeline.services.llms.gemini_interface import GeminiInterface
from us_healthcare_pipeline.services.llms.perplexity_interface import PerplexityInterface
from us_healthcare_pipeline.config.questions import questions


def generate_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True, help="City name, e.g. 'New York'")
    parser.add_argument("--persona", required=True, help="Persona label: left, right, neutral")
    parser.add_argument("--llm", choices=["chatgpt", "gemini", "perplexity"], default="chatgpt", help="LLM to use")
    parser.add_argument("--base_results_dir", default=None, help="Shared base results directory (optional)")
    args = parser.parse_args()

    # Use passed base dir or create a new timestamped one
    if args.base_results_dir:
        base_results_dir = args.base_results_dir
    else:
        base_results_dir = os.path.join("us_healthcare_pipeline/results", generate_timestamp())
        os.makedirs(base_results_dir, exist_ok=True)

    # Subdirectory per run
    run_output_dir = os.path.join(
        base_results_dir,
        f"{args.city.lower().replace(' ', '_')}_{args.persona.lower()}_{args.llm.lower()}"
    )
    os.makedirs(run_output_dir, exist_ok=True)

    print(f"[INFO] Starting session at: {run_output_dir}")

    session = SessionManager(
        city_name=args.city,
        persona_label=args.persona,
        base_results_dir=run_output_dir
    )

    # Instantiate the appropriate LLM interface
    if args.llm == "gemini":
        llm = GeminiInterface()
    elif args.llm == "perplexity":
        llm = PerplexityInterface()
    else:
        llm = ChatGPTInterface()

    print("[INFO] Running browsing and LLM interaction phase...")
    browser_result, llm_responses = session.run_session(llm, questions)

    print("[INFO] Session complete.")
    print("[INFO] Visited URLs:")
    for url in browser_result.visited_urls:
        print(" -", url)

    if llm_responses:
        print("[INFO] Sample response:")
        print(f"Q: {llm_responses[0].question}")
        print(f"A: {llm_responses[0].answer[:200]}...")


if __name__ == "__main__":
    main()

