#!/usr/bin/env python3
"""
Generate summaries for CNN/DM samples using H2OGPTE.
Reads cnn_dm_sample.json and creates summaries for each article.
"""

import os
import json
from dotenv import load_dotenv
from pathlib import Path
from h2ogpte import H2OGPTE

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv('H2OGPTE_API_KEY')
ADDRESS = os.getenv('H2OGPTE_ADDRESS')
LLM_MODEL = 'gpt-4o'

if not API_KEY or not ADDRESS:
    print("❌ Error: H2OGPTE_API_KEY and H2OGPTE_ADDRESS must be set in .env file")
    exit(1)

print("="*80)
print("H2OGPTE API Testing")
print("="*80)
print(f"\n📍 Address: {ADDRESS}")
print(f"🔑 API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print()


def generate_summaries(
    input_file="cnn_dm_sample.json",
    output_file="cnn_dm_with_generated_summaries.json",
    h2ogpte_address='https://your-h2ogpte-server-address',
    api_key='your-api-key-here',
    llm='gpt-4o'
):
    """
    Generate summaries for articles in the CNN/DM sample file.

    Args:
        input_file: Input JSON file with CNN/DM samples
        output_file: Output JSON file with generated summaries
        h2ogpte_address: H2OGPTE server address
        api_key: API key for H2OGPTE
        llm: Model to use for summarization
    """
    # Setup paths
    script_dir = Path(__file__).parent
    input_path = script_dir.parent / "raw" / input_file
    output_path = script_dir.parent / "processed" / output_file

    # 1. Setup H2OGPTE Client
    print("Setting up H2OGPTE client...")
    client = H2OGPTE(
        address=h2ogpte_address,
        api_key=api_key
    )

    # Check available models
    print(f"Using model: {llm}")

    # 2. Load the CNN/DM samples
    print(f"\nLoading samples from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} samples")

    # 3. Generate summaries for each article
    results = []
    for i, item in enumerate(data):
        article_id = item.get('id', f'sample_{i}')
        source_text = item.get('source', '')
        reference_summary = item.get('summary', '')

        print(f"\n[{i+1}/{len(data)}] Processing: {article_id}")
        print(f"  Article length: {len(source_text)} characters")

        try:
            # Generate summary using H2OGPTE
            summary_response = client.summarize_content(
                text_context_list=[source_text],
                llm=llm,
                pre_prompt_summary="Please read the following news article carefully:",
                prompt_summary="Provide a concise summary highlighting the main points and key facts from the article above."
            )

            if summary_response.content:
                generated_summary = summary_response.content
                print(f"  ✓ Generated summary: {len(generated_summary)} characters")
            else:
                generated_summary = f"Error: {summary_response.error}"
                print(f"  ✗ Error: {summary_response.error}")

        except Exception as e:
            generated_summary = f"Exception: {str(e)}"
            print(f"  ✗ Exception: {e}")

        # Store result with both reference and generated summaries
        result = {
            "id": article_id,
            "source": source_text,
            "reference_summary": reference_summary,
            "summary": generated_summary
        }
        results.append(result)

    # 4. Save results
    print(f"\nSaving results to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Successfully saved {len(results)} samples with generated summaries")
    print(f"\nOutput structure:")
    print(f"  - id: Document identifier")
    print(f"  - source: Full article text")
    print(f"  - reference_summary: Original CNN/DM highlights")
    print(f"  - generated_summary: H2OGPTE generated summary")

if __name__ == "__main__":
    generate_summaries(
        input_file="cnn_dm_sample.json",
        output_file="cnn_dm_sample_with_gen_sum.json",
        h2ogpte_address=ADDRESS,
        api_key=API_KEY,
        llm=LLM_MODEL
    )
