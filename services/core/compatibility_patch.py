"""
兼容性补丁 - 修复transformers版本兼容性问题
"""
import warnings

# 在导入sentence-transformers之前修复兼容性问题
try:
    import transformers
    # 如果transformers版本太旧，添加缺失的属性
    if not hasattr(transformers, 'is_torch_npu_available'):
        transformers.is_torch_npu_available = lambda: False
        warnings.warn("transformers版本较旧，已添加兼容性补丁", UserWarning)
except ImportError:
    pass

# 现在可以安全导入sentence-transformers
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
except ImportError as e:
    warnings.warn(f"sentence-transformers导入失败: {e}", UserWarning)

