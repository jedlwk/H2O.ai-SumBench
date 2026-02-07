"""
Force CPU-only mode for all PyTorch operations.
This must be imported BEFORE any other imports in the application.
"""
import os
import sys

# Force CPU mode - set BEFORE any imports (multiple variations for maximum compatibility)
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Disable CUDA in PyTorch (if not yet imported)
os.environ['USE_CUDA'] = '0'
os.environ['FORCE_CPU'] = '1'

# Suppress noisy HuggingFace / Transformers warnings:
# - Unauthenticated HF Hub requests warning
# - Safetensors auto-conversion background thread errors
# - "loss_type=None" config warnings
# - UNEXPECTED/MISSING weight load reports
# - "The following layers were not sharded" from accelerate
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
os.environ['ACCELERATE_DISABLE_RICH'] = '1'

import warnings
import logging
import threading

warnings.filterwarnings('ignore', message='.*UNEXPECTED.*')
warnings.filterwarnings('ignore', message='.*MISSING.*')
warnings.filterwarnings('ignore', message='.*loss_type.*')
warnings.filterwarnings('ignore', message='.*safetensors.*')
warnings.filterwarnings('ignore', message='.*layers were not sharded.*')
warnings.filterwarnings('ignore', message='.*unauthenticated.*')

logging.getLogger('transformers.modeling_utils').setLevel(logging.ERROR)
logging.getLogger('transformers.integrations.tensor_parallel').setLevel(logging.ERROR)
logging.getLogger('accelerate.utils.modeling').setLevel(logging.ERROR)
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)

# Silence the safetensors auto-conversion background thread exception
_original_threading_excepthook = threading.excepthook
def _quiet_threading_excepthook(args):
    if args.exc_type is OSError and 'safetensors' in str(args.exc_value):
        return  # Suppress safetensors conversion PR errors
    _original_threading_excepthook(args)
threading.excepthook = _quiet_threading_excepthook

# Filter stderr to suppress noisy messages that bypass Python logging
# (e.g. HF Hub unauthenticated warning, progress bar residuals)
class _StderrFilter:
    """Wraps stderr to suppress known noisy messages from third-party libs."""
    _suppress = ('unauthenticated', 'layers were not sharded', 'Loading weights:')

    def __init__(self, stream):
        self._stream = stream

    def write(self, text):
        if any(s in text for s in self._suppress):
            return len(text)
        return self._stream.write(text)

    def flush(self):
        self._stream.flush()

    def __getattr__(self, name):
        return getattr(self._stream, name)

sys.stderr = _StderrFilter(sys.stderr)

# Verify PyTorch will use CPU (if already installed)
try:
    import torch
    if torch.cuda.is_available():
        print("WARNING: CUDA is still available after forcing CPU mode!", file=sys.stderr)
    else:
        print("CPU-only mode enforced successfully", file=sys.stderr)
except ImportError:
    # PyTorch not yet installed - this is fine during initial setup
    print("CPU environment variables set (PyTorch not yet loaded)", file=sys.stderr)
