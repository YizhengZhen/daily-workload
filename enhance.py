#!/usr/bin/env python3
"""
AI enhancement with semantic scoring based on research directions.
Processes JSONL from fetch_rss.py, calls LLM for analysis, and outputs enhanced JSONL.
"""
import os
import json
import sys
import yaml
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import argparse

import langchain_core.exceptions
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from structure import PaperAnalysis


def load_config(config_path: str = "config.yaml") -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_research_directions(directions_path: str = "research_directions.md") -> str:
    """Load research directions from markdown file."""
    if not os.path.exists(directions_path):
        print(f"Warning: Research directions file not found: {directions_path}", file=sys.stderr)
        return "General research papers"
    
    with open(directions_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove markdown headers and keep bullet points
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('##'):
            lines.append(line)
    
    return '\n'.join(lines)


def create_prompt_template(config: Dict, research_directions: str) -> ChatPromptTemplate:
    """Create the prompt template with system and human messages."""
    # Load system prompt template
    system_template = open("ai_system.txt", "r").read()
    
    # Get threshold from config
    threshold = config.get('scoring', {}).get('threshold', 6.0)
    
    # Format system template with actual values
    system_content = system_template.format(
        threshold=threshold,
        research_directions=research_directions
    )
    
    # Human template - simple abstract analysis
    human_template = """Analyze the following paper abstract:

Title: {title}

Abstract:
{abstract}

Please provide your analysis based on the research directions provided earlier."""

    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_content),
        HumanMessagePromptTemplate.from_template(human_template)
    ])


def process_single_item(chain, item: Dict, config: Dict) -> Dict:
    """Process a single paper item with AI analysis."""
    default_analysis = {
        "tldr": "Analysis failed",
        "motivation": "Not analyzed",
        "method": "Not analyzed",
        "result": "Not analyzed",
        "conclusion": "Not analyzed",
        "score": 0.0,
        "recommendation": False,
        "reasoning": "Analysis failed",
        "key_contributions": "",
        "limitations": "",
        "follow_up_questions": ""
    }
    
    try:
        # Extract title and abstract
        title = item.get('title', 'Untitled')
        abstract = item.get('summary', '')
        
        if not abstract or abstract.strip() == '':
            print(f"Warning: Empty abstract for {title}", file=sys.stderr)
            item['AI'] = default_analysis
            return item
        
        # Invoke LLM
        response: PaperAnalysis = chain.invoke({
            "title": title,
            "abstract": abstract
        })
        
        # Convert to dict
        analysis_dict = response.model_dump()
        
        # Ensure all fields exist
        for key in default_analysis.keys():
            if key not in analysis_dict:
                analysis_dict[key] = default_analysis[key]
        
        item['AI'] = analysis_dict
        return item
        
    except langchain_core.exceptions.OutputParserException as e:
        print(f"Output parsing error for {item.get('id', 'unknown')}: {e}", file=sys.stderr)
        item['AI'] = default_analysis
        return item
    except Exception as e:
        print(f"Unexpected error for {item.get('id', 'unknown')}: {e}", file=sys.stderr)
        item['AI'] = default_analysis
        return item


def process_all_items(data: List[Dict], config: Dict, research_directions: str) -> List[Dict]:
    """Process all data items in parallel."""
    # Setup LLM
    llm_config = config.get('llm', {})
    model_name = llm_config.get('model_name', 'deepseek-chat')
    base_url = llm_config.get('base_url', 'https://api.deepseek.com')
    temperature = llm_config.get('temperature', 0.3)
    
    llm = ChatOpenAI(
        model=model_name,
        base_url=base_url,
        temperature=temperature,
        max_tokens=llm_config.get('max_tokens', 1000)
    ).with_structured_output(PaperAnalysis, method="function_calling")
    
    print(f"Connected to: {model_name} at {base_url}", file=sys.stderr)
    
    # Create prompt chain
    prompt_template = create_prompt_template(config, research_directions)
    chain = prompt_template | llm
    
    # Determine max workers (default to 1 for rate limiting)
    max_workers = config.get('processing', {}).get('max_workers', 1)
    
    # Process in parallel
    processed_data = [None] * len(data)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(process_single_item, chain, item, config): idx
            for idx, item in enumerate(data)
        }
        
        # Process with progress bar
        for future in tqdm(
            as_completed(future_to_idx),
            total=len(data),
            desc="AI processing papers"
        ):
            idx = future_to_idx[future]
            try:
                processed_data[idx] = future.result()
            except Exception as e:
                print(f"Item at index {idx} failed: {e}", file=sys.stderr)
                processed_data[idx] = data[idx]
                processed_data[idx]['AI'] = {
                    "tldr": "Processing failed",
                    "motivation": "Processing failed",
                    "method": "Processing failed",
                    "result": "Processing failed",
                    "conclusion": "Processing failed",
                    "score": 0.0,
                    "recommendation": False,
                    "reasoning": "Processing failed"
                }
    
    return processed_data


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="JSONL data file from fetch_rss.py")
    parser.add_argument("--config", type=str, default="config.yaml", help="Configuration file path")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Load research directions
    directions_path = config.get('scoring', {}).get('fields', 'research_directions.md')
    research_directions = load_research_directions(directions_path)
    
    # Read input data
    data = []
    with open(args.data, "r", encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    print(f"Loaded {len(data)} papers for AI processing", file=sys.stderr)
    
    # Remove existing output file if present
    language = config.get('processing', {}).get('language', 'English')
    output_file = args.data.replace('.jsonl', f'_AI_enhanced_{language}.jsonl')
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed existing file: {output_file}", file=sys.stderr)
    
    # Process data
    processed_data = process_all_items(data, config, research_directions)
    
    # Filter out None results (shouldn't happen with error handling)
    processed_data = [item for item in processed_data if item is not None]
    
    # Write output
    with open(output_file, "w", encoding='utf-8') as f:
        for item in processed_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Saved {len(processed_data)} enhanced papers to {output_file}", file=sys.stderr)
    
    # Print statistics
    scores = [item.get('AI', {}).get('score', 0.0) for item in processed_data]
    recommendations = [item.get('AI', {}).get('recommendation', False) for item in processed_data]
    
    if scores:
        avg_score = sum(scores) / len(scores)
        recommended = sum(recommendations)
        print(f"\nStatistics:", file=sys.stderr)
        print(f"  Average score: {avg_score:.2f}/10", file=sys.stderr)
        print(f"  Recommended papers: {recommended}/{len(processed_data)}", file=sys.stderr)
        print(f"  Recommendation rate: {recommended/len(processed_data)*100:.1f}%", file=sys.stderr)
    
    return output_file


if __name__ == "__main__":
    main()