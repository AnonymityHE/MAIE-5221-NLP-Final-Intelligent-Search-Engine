"""
MLX LM支持（Mac优化）
用于在Mac上使用MLX优化的语言模型
"""
from typing import Optional, Dict, List
from services.core.logger import logger

try:
    from mlx_lm import load, generate
    import mlx.core as mx
    MLX_LM_AVAILABLE = True
except ImportError:
    MLX_LM_AVAILABLE = False
    logger.debug("mlx-lm未安装，MLX LM功能不可用")


class MLXLMModel:
    """MLX LM模型封装（Mac优化）"""
    
    def __init__(self, model_name: str = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"):
        """
        初始化MLX LM模型
        
        Args:
            model_name: 模型名称（HuggingFace Hub上的MLX模型）
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
        if not MLX_LM_AVAILABLE:
            logger.warning("mlx-lm未安装，无法使用MLX LM")
            logger.info("安装命令: pip install mlx-lm")
            return
        
        try:
            logger.info(f"正在加载MLX LM模型: {model_name}")
            # 注意：某些模型可能有tokenizer兼容性问题
            # 如果加载失败，可以尝试其他模型
            self.model, self.tokenizer = load(model_name)
            logger.info("✅ MLX LM模型加载成功")
        except AttributeError as e:
            # 处理tokenizer兼容性问题（chat_template属性）
            logger.warning(f"MLX LM模型加载遇到兼容性问题: {e}")
            logger.info("尝试使用其他模型或更新transformers版本")
            self.model = None
            self.tokenizer = None
        except Exception as e:
            logger.error(f"MLX LM模型加载失败: {e}")
            logger.info("提示: 可以尝试更新transformers版本: pip install --upgrade transformers")
            self.model = None
            self.tokenizer = None
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = False
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            max_tokens: 最大token数
            temperature: 温度参数
            top_p: 核采样参数
            stream: 是否流式输出
            
        Returns:
            生成的文本
        """
        if not self.model or not self.tokenizer:
            return ""
        
        try:
            if stream:
                # 流式生成
                response = ""
                for token in generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temp=temperature,
                    top_p=top_p,
                    verbose=False
                ):
                    response += token
                    yield token
                return response
            else:
                # 非流式生成
                response = generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temp=temperature,
                    top_p=top_p,
                    verbose=False
                )
                return response
        except Exception as e:
            logger.error(f"MLX LM生成失败: {e}")
            return ""
    
    def is_available(self) -> bool:
        """检查模型是否可用"""
        return self.model is not None and self.tokenizer is not None


# 全局MLX LM实例
_mlx_lm_model: Optional[MLXLMModel] = None


def get_mlx_lm(model_name: str = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit") -> Optional[MLXLMModel]:
    """获取MLX LM实例"""
    global _mlx_lm_model
    
    if _mlx_lm_model is None:
        _mlx_lm_model = MLXLMModel(model_name=model_name)
    
    return _mlx_lm_model if _mlx_lm_model.is_available() else None

