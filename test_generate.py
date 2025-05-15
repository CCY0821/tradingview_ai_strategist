import sys
import os
import logging
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.strategy_generator import StrategyGenerator

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_strategy_generation():
    """測試策略生成功能"""
    try:
        # 初始化策略生成器
        generator = StrategyGenerator()
        
        # 測試不同類型的策略生成
        test_cases = [
            "產生一個 Bollinger Band 策略",
            "創建一個結合 RSI 和 MACD 的策略",
            "設計一個移動平均交叉策略"
        ]
        
        for prompt in test_cases:
            logger.info(f"\n測試案例: {prompt}")
            logger.info("-" * 50)
            
            # 生成策略
            strategy = generator.generate_new_strategy(prompt)
            
            # 輸出結果
            logger.info("生成的策略代碼:")
            print(strategy.get('pine_script', '無策略代碼'))
            logger.info("\n策略說明:")
            print(strategy.get('description', '無說明'))
            logger.info("=" * 50)
            
    except Exception as e:
        logger.error(f"策略生成測試失敗: {str(e)}")
        raise

if __name__ == "__main__":
    test_strategy_generation() 