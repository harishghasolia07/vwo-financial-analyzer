import sys
import asyncio
from main import run_crew

def test():
    # We assume 'data/sample.pdf' exists or we can create a dummy PDF.
    try:
        result = run_crew("What is the company's revenue?", "data/sample.pdf")
        print("PIPELINE RESULT:")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
