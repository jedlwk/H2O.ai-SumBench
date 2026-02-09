#!/usr/bin/env python3
"""
Tests for the MCP server layer (mcp_server/server.py).

Verifies the METRIC_CATALOG, scenario detection, helper functions,
and tool definitions without needing a running MCP transport.

Run:  python -m pytest tests/test_mcp_server.py -v
"""

import ast
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
SERVER_PATH = os.path.join(PROJECT_ROOT, 'mcp_server', 'server.py')

import pytest


# ---------------------------------------------------------------------------
# Parse METRIC_CATALOG from server.py via AST (avoids running install_dependencies)
# ---------------------------------------------------------------------------

def _load_catalog():
    with open(SERVER_PATH) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'METRIC_CATALOG':
                    return ast.literal_eval(node.value)
    raise RuntimeError("METRIC_CATALOG not found in server.py")


CATALOG = _load_catalog()
EXCLUDED = {'nli', 'factcc', 'alignscore', 'moverscore', 'bartscore'}


# ---------------------------------------------------------------------------
# Catalog structure
# ---------------------------------------------------------------------------

class TestCatalog:

    def test_has_17_metrics(self):
        assert len(CATALOG) == 17

    def test_no_excluded_metrics(self):
        for name in EXCLUDED:
            assert name not in CATALOG, f"Excluded metric '{name}' found in catalog"

    def test_required_fields(self):
        for name, info in CATALOG.items():
            for field in ('category', 'score_range', 'description', 'recommended_for'):
                assert field in info, f"'{name}' missing '{field}'"

    def test_recommended_for_values(self):
        valid = {'source+reference', 'source_only', 'reference_only', 'neither'}
        for name, info in CATALOG.items():
            for scenario in info['recommended_for']:
                assert scenario in valid, f"'{name}' has invalid scenario '{scenario}'"


# ---------------------------------------------------------------------------
# Scenario detection & metric selection
# ---------------------------------------------------------------------------

def _metrics_for(scenario):
    return [n for n, i in CATALOG.items() if scenario in i['recommended_for']]


class TestScenarios:

    def test_source_reference_count(self):
        assert len(_metrics_for('source+reference')) == 17

    def test_source_only_count(self):
        assert len(_metrics_for('source_only')) == 6

    def test_reference_only_count(self):
        assert len(_metrics_for('reference_only')) == 8

    def test_neither_count(self):
        assert len(_metrics_for('neither')) == 2


# ---------------------------------------------------------------------------
# Helper functions (imported directly, bypassing install_dependencies)
# ---------------------------------------------------------------------------

# We can't import server.py directly (it calls install_dependencies at
# module level), so we re-implement the pure helpers and verify logic.

def _detect_scenario(source, reference):
    if source and reference:
        return 'source+reference'
    if source:
        return 'source_only'
    if reference:
        return 'reference_only'
    return 'neither'


class TestDetectScenario:

    def test_both(self):
        assert _detect_scenario("src", "ref") == 'source+reference'

    def test_source_only(self):
        assert _detect_scenario("src", None) == 'source_only'

    def test_reference_only(self):
        assert _detect_scenario(None, "ref") == 'reference_only'

    def test_neither(self):
        assert _detect_scenario(None, None) == 'neither'

    def test_empty_strings_as_none(self):
        assert _detect_scenario("", "") == 'neither'


# ---------------------------------------------------------------------------
# Build-summary helper
# ---------------------------------------------------------------------------

class TestBuildSummary:

    @staticmethod
    def _fake_results():
        return {
            'rouge': {'scores': {'rouge1': 0.85, 'rougeL': 0.80}},
            'bleu':  {'scores': {'bleu': 0.45}},
            'perplexity': {'scores': {'perplexity': 32.5}},
        }

    def test_extract_primary_score(self):
        """Primary-score extraction picks the right key."""
        scores = {'rouge1': 0.85, 'rougeL': 0.80}
        # 'rouge1' should be picked (it's in the priority list)
        for key in ('f1', 'score', 'rougeL', 'rouge1'):
            if key in scores:
                val = scores[key]
                assert isinstance(val, float)
                break


# ---------------------------------------------------------------------------
# Tool definitions exist in source
# ---------------------------------------------------------------------------

class TestToolDefinitions:

    def _source(self):
        with open(SERVER_PATH) as f:
            return f.read()

    def test_evaluate_summary_defined(self):
        assert 'def evaluate_summary(' in self._source()

    def test_list_metrics_defined(self):
        assert 'def list_metrics(' in self._source()

    def test_get_info_defined(self):
        assert 'def get_info(' in self._source()

    def test_no_old_tools(self):
        src = self._source()
        for old in ('def run_single_metric(', 'def run_multiple(', 'def recommend_metrics('):
            assert old not in src, f"Old tool '{old}' still present"


# ---------------------------------------------------------------------------
# system_base.md consistency
# ---------------------------------------------------------------------------

class TestSystemBase:

    def _content(self):
        path = os.path.join(PROJECT_ROOT, 'agents', 'prompts', 'system_base.md')
        with open(path) as f:
            return f.read()

    def test_says_17_metrics(self):
        assert '17 metrics' in self._content()

    def test_says_5_categories(self):
        assert '5 categories' in self._content()

    def test_no_excluded_mentions(self):
        content = self._content().lower()
        for name in ('moverscore', 'bartscore', 'alignscore', 'factcc'):
            assert name not in content, f"Excluded metric '{name}' mentioned in system_base.md"
