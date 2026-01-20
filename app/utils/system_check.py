"""
AIEAT System Check - Hardware detection for model selection.

Detects:
- CPU (cores, speed)
- GPU (CUDA, VRAM)
- RAM (total, available)
- NPU (if available)
- OpenGL version

Returns JSON for dynamic model selection.
"""
import platform
import subprocess
import json
from typing import Dict, Any, Optional

from app.utils.logger import get_app_logger

logger = get_app_logger(__name__)


def get_cpu_info() -> Dict[str, Any]:
    """Get CPU information."""
    info = {
        'processor': platform.processor(),
        'machine': platform.machine(),
        'cores_logical': None,
        'cores_physical': None,
    }
    
    try:
        import psutil
        info['cores_logical'] = psutil.cpu_count(logical=True)
        info['cores_physical'] = psutil.cpu_count(logical=False)
    except ImportError:
        pass
    
    return info


def get_gpu_info() -> Dict[str, Any]:
    """Get GPU information."""
    info = {
        'available': False,
        'name': None,
        'memory_mb': None,
        'cuda_available': False,
        'cuda_version': None,
    }
    
    # Try nvidia-smi first
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(', ')
            if len(parts) >= 2:
                info['available'] = True
                info['name'] = parts[0]
                try:
                    info['memory_mb'] = int(float(parts[1]))
                except (ValueError, IndexError):
                    pass
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try PyTorch for CUDA info
    try:
        import torch
        info['cuda_available'] = torch.cuda.is_available()
        if info['cuda_available']:
            info['cuda_version'] = torch.version.cuda
            if not info['name']:
                info['name'] = torch.cuda.get_device_name(0)
            if not info['memory_mb']:
                info['memory_mb'] = int(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024))
            info['available'] = True
    except ImportError:
        pass
    
    return info


def get_ram_info() -> Dict[str, Any]:
    """Get RAM information."""
    info = {
        'total_gb': None,
        'available_gb': None,
        'percent_used': None,
    }
    
    try:
        import psutil
        mem = psutil.virtual_memory()
        info['total_gb'] = round(mem.total / (1024**3), 1)
        info['available_gb'] = round(mem.available / (1024**3), 1)
        info['percent_used'] = mem.percent
    except ImportError:
        pass
    
    return info


def get_opengl_info() -> Dict[str, Any]:
    """Get OpenGL information."""
    info = {
        'available': False,
        'version': None,
    }
    
    # OpenGL detection is platform-specific and complex
    # For now, just check if PyOpenGL is installed
    try:
        import OpenGL
        info['available'] = True
        info['version'] = getattr(OpenGL, '__version__', 'Unknown')
    except ImportError:
        pass
    
    return info


def get_system_info() -> Dict[str, Any]:
    """Get complete system information."""
    info = {
        'os': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
        },
        'python': {
            'version': platform.python_version(),
        },
        'cpu': get_cpu_info(),
        'gpu': get_gpu_info(),
        'ram': get_ram_info(),
        'opengl': get_opengl_info(),
    }
    
    # Add recommendations based on capabilities
    info['recommendations'] = get_model_recommendations(info)
    
    return info


def get_model_recommendations(system_info: Dict) -> Dict[str, Any]:
    """Get model recommendations based on system capabilities."""
    gpu_info = system_info.get('gpu', {})
    ram_info = system_info.get('ram', {})
    
    recommendations = {
        'can_run_local_llm': False,
        'max_model_size_b': 0,
        'recommended_scoring_model': None,
        'recommended_translation_model': None,
        'use_gpu': False,
        'notes': [],
    }
    
    # Check GPU
    if gpu_info.get('cuda_available'):
        vram_mb = gpu_info.get('memory_mb', 0)
        recommendations['use_gpu'] = True
        
        if vram_mb >= 24000:  # 24GB+
            recommendations['max_model_size_b'] = 13
            recommendations['recommended_scoring_model'] = 'Qwen2.5-7B-Instruct'
            recommendations['recommended_translation_model'] = 'OpenThaiGPT-13B'
        elif vram_mb >= 16000:  # 16GB+
            recommendations['max_model_size_b'] = 8
            recommendations['recommended_scoring_model'] = 'Qwen2.5-3B-Instruct'
            recommendations['recommended_translation_model'] = 'Typhoon-8B'
        elif vram_mb >= 8000:  # 8GB+
            recommendations['max_model_size_b'] = 4
            recommendations['recommended_scoring_model'] = 'Qwen2.5-1.5B-Instruct'
            recommendations['recommended_translation_model'] = 'Typhoon-4B'
            recommendations['notes'].append('8GB VRAM: Can run 1-4B models with LoRA fine-tuning')
        elif vram_mb >= 4000:  # 4GB+
            recommendations['max_model_size_b'] = 2
            recommendations['recommended_scoring_model'] = 'TinyLlama-1.1B'
            recommendations['recommended_translation_model'] = 'Qwen2.5-1.5B-Instruct'
            recommendations['notes'].append('Limited VRAM: Use quantized models only')
        
        recommendations['can_run_local_llm'] = vram_mb >= 4000
    
    # Check RAM for CPU fallback
    ram_gb = ram_info.get('total_gb', 0)
    if not recommendations['can_run_local_llm'] and ram_gb >= 16:
        recommendations['can_run_local_llm'] = True
        recommendations['max_model_size_b'] = 2
        recommendations['recommended_scoring_model'] = 'TinyLlama-1.1B (CPU)'
        recommendations['notes'].append('No GPU: Using CPU inference (slow)')
    
    return recommendations


def print_system_report():
    """Print a formatted system report."""
    info = get_system_info()
    
    print("=" * 60)
    print("AIEAT SYSTEM CHECK")
    print("=" * 60)
    
    print(f"\n[OS] {info['os']['system']} {info['os']['release']}")
    print(f"[Python] {info['python']['version']}")
    
    cpu = info['cpu']
    print(f"\n[CPU] {cpu['processor']}")
    if cpu['cores_logical']:
        print(f"   Cores: {cpu['cores_physical']} physical, {cpu['cores_logical']} logical")
    
    gpu = info['gpu']
    if gpu['available']:
        print(f"\n[GPU] {gpu['name']}")
        print(f"   VRAM: {gpu['memory_mb']} MB")
        if gpu['cuda_available']:
            print(f"   CUDA: {gpu['cuda_version']} [OK]")
    else:
        print("\n[GPU] Not available")
    
    ram = info['ram']
    if ram['total_gb']:
        print(f"\n[RAM] {ram['total_gb']} GB total, {ram['available_gb']} GB available")
    
    rec = info['recommendations']
    print("\n[RECOMMENDATIONS]")
    print(f"   Can run local LLM: {'Yes' if rec['can_run_local_llm'] else 'No'}")
    if rec['can_run_local_llm']:
        print(f"   Max model size: {rec['max_model_size_b']}B parameters")
        print(f"   Scoring model: {rec['recommended_scoring_model']}")
        print(f"   Translation model: {rec['recommended_translation_model']}")
    for note in rec.get('notes', []):
        print(f"   Note: {note}")
    
    print("=" * 60)
    
    return info


# Export as JSON
def get_system_info_json() -> str:
    """Get system info as JSON string."""
    return json.dumps(get_system_info(), indent=2)


# CLI entry point
if __name__ == "__main__":
    print_system_report()
