#!/usr/bin/env python3
"""
Command Line Interface for Multi-Agent System Advisor

This script provides a command-line interface to the multi-agent system advisor,
allowing users to run analysis without the web interface.

Usage:
    python cli.py "Your question here"
    python cli.py --interactive
"""

import sys
import asyncio
import argparse
from src.advisor_logic import ooda_run, METRICS

def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent System Advisor - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cli.py "Compare Raft vs PBFT for financial trading"
    python cli.py --interactive
    python cli.py --help
        """
    )
    
    parser.add_argument(
        'question',
        nargs='?',
        help='The technical question to analyze'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--model',
        default='llama3:latest',
        help='Ollama model to use (default: llama3:latest)'
    )
    
    args = parser.parse_args()
    
    # Set model if specified
    import os
    if args.model:
        os.environ['MODEL'] = args.model
    
    print("\n🎓 Multi-Agent System Advisor - CLI")
    print("=" * 50)
    
    if args.interactive:
        run_interactive_mode()
    elif args.question:
        run_single_question(args.question)
    else:
        print("Error: Please provide a question or use --interactive mode")
        print("Use --help for more information")
        sys.exit(1)

def run_single_question(question):
    """Run analysis for a single question"""
    print(f"\n🔄 Processing: {question}")
    print("-" * 50)
    
    try:
        asyncio.run(ooda_run(question))
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        print(f"\n📊 Final Metrics: {METRICS.summary()}")

def run_interactive_mode():
    """Run in interactive mode"""
    print("\n🔄 Interactive Mode")
    print("Type 'quit', 'exit', or press Ctrl+C to exit")
    print("=" * 50)
    
    example_questions = [
        "Compare Raft vs PBFT consensus algorithms for financial trading systems",
        "How do multi-agent systems handle Byzantine fault tolerance?",
        "What are the performance implications of consensus algorithms in HFT?"
    ]
    
    print("\n💡 Example questions:")
    for i, q in enumerate(example_questions, 1):
        print(f"  {i}. {q}")
    print()
    
    while True:
        try:
            question = input("\n> Enter your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not question:
                print("Please enter a question.")
                continue
                
            # Check if user entered a number for example questions
            if question.isdigit():
                num = int(question)
                if 1 <= num <= len(example_questions):
                    question = example_questions[num - 1]
                    print(f"Using example: {question}")
                else:
                    print("Invalid example number.")
                    continue
            
            print(f"\n🔄 Processing: {question}")
            print("-" * 50)
            
            # Reset metrics for each question
            METRICS.llm_tokens_in = 0
            METRICS.llm_tokens_out = 0
            METRICS.tool_calls = {"search": 0, "fetch": 0, "vector": 0}
            METRICS.cache_hits = {"search": 0, "fetch": 0}
            METRICS.events = []
            METRICS.error_count = 0
            METRICS.start_time = time.time()
            
            asyncio.run(ooda_run(question))
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    import time
    main()

