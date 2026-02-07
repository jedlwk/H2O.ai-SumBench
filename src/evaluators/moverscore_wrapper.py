"""
MoverScore wrapper using vendored moverscore_v2_patched.

The vendored copy (moverscore_v2_patched.py) contains two critical patches:
  - Auto-detect CPU/CUDA instead of hardcoded 'cuda:0'
  - Use tokenizer.model_max_length instead of deprecated tokenizer.max_len
"""

from .moverscore_v2_patched import word_mover_score, get_idf_dict

__all__ = ['word_mover_score', 'get_idf_dict']
