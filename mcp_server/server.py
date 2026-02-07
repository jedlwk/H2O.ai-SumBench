"""
Build an MCP server for H2O.ai SumBench.
"""

import os
import sys
import subprocess

# Install dependencies before importing local modules
def install_dependencies():
    """Install dependencies from requirements.txt if present."""
    server_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(server_dir, 'requirements.txt')

    if os.path.exists(requirements_path):
        print(f"[MCP Server] Installing dependencies from {requirements_path}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "-r", requirements_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("[MCP Server] Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[MCP Server] Warning: Failed to install dependencies: {e}")
            print("[MCP Server] Continuing with existing packages...")
    else:
        print(f"[MCP Server] No requirements.txt found at {requirements_path}")

# Install dependencies before any local imports
install_dependencies()

from mcp.server.fastmcp import FastMCP

# Try/except imports for both development and bundled modes
try:
    # Development mode: src/ is in parent directory
    from src.evaluators.tool_logic import (
        list_available_metrics,
        run_metric,
        run_multiple_metrics,
        get_metric_info,
    )
except ImportError:
    # Bundled mode: evaluators/ is directly accessible
    from evaluators.tool_logic import (
        list_available_metrics,
        run_metric,
        run_multiple_metrics,
        get_metric_info,
    )

mcp = FastMCP("H2O.ai SumBench MCP Server")

# Metrics that work reliably on any input length.
# Excluded: nli, factcc, alignscore, moverscore, bartscore (truncate at 512-1024 tokens).
SUPPORTED_METRICS = {
    # Word overlap (no length limit)
    'rouge', 'bleu', 'meteor', 'levenshtein', 'chrf',
    # Fluency (evaluates summary only)
    'perplexity',
    # Semantic (library handles chunking internally)
    'bertscore',
    # Completeness (sentence-level / NER, no length limit)
    'entity_coverage', 'semantic_coverage', 'bertscore_recall',
    # LLM judge (H2OGPTE LLM handles long context)
    'llm_faithfulness', 'llm_coherence', 'llm_relevance', 'llm_fluency',
    'llm_dag', 'llm_prometheus', 'factchecker_api',
}


@mcp.tool()
def list_metrics():
    """List available evaluation metrics (only length-safe metrics are exposed)."""
    all_metrics = list_available_metrics()
    return [m for m in all_metrics if m.get('name', m) in SUPPORTED_METRICS]


@mcp.tool()
def run_single_metric(metric_name: str, summary: str, source: str = None, reference: str = None):
    """Run a single evaluation metric. Only length-safe metrics are allowed."""
    if metric_name not in SUPPORTED_METRICS:
        return {'error': f"Metric '{metric_name}' is not available. Use list_metrics() to see supported metrics."}
    return run_metric(metric_name, summary, source, reference)


@mcp.tool()
def run_multiple(metrics: list, summary: str, source: str = None, reference: str = None):
    """Run multiple evaluation metrics at once. Unsupported metrics are skipped."""
    safe = [m for m in metrics if m in SUPPORTED_METRICS]
    skipped = [m for m in metrics if m not in SUPPORTED_METRICS]
    results = run_multiple_metrics(safe, summary, source, reference)
    if skipped:
        results['_skipped'] = {m: 'Not available (token length limit)' for m in skipped}
    return results


@mcp.tool()
def get_info(metric_name: str):
    """Get detailed information about a specific metric."""
    return get_metric_info(metric_name)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
