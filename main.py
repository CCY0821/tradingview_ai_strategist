import logging
from pathlib import Path
from database.db_handler import DatabaseHandler
from database.strategy_db import DatabaseManager
from core.strategy_generator import StrategyGenerator

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """初始化數據庫"""
    try:
        db_manager = DatabaseManager()
        logger.info("數據庫初始化成功")
        return db_manager
    except Exception as e:
        logger.error(f"數據庫初始化失敗: {str(e)}")
        raise

def save_example_strategy(db_manager):
    """保存示例策略"""
    try:
        # 示例策略代碼
        example_strategy = {
            "description": "Bollinger Bands 交易策略",
            "pine_script": """//@version=5
strategy("Bollinger Bands Strategy", overlay=true)

// 參數設置
length = input.int(20, "BB Length")
mult = input.float(2.0, "BB Std Dev")

// 計算 Bollinger Bands
[middle, upper, lower] = ta.bb(close, length, mult)

// 交易邏輯
longCondition = close < lower
shortCondition = close > upper

// 執行交易
if (longCondition)
    strategy.entry("BB Long", strategy.long)

if (shortCondition)
    strategy.entry("BB Short", strategy.short)

// 繪製指標
plot(middle, "Middle Band", color=color.blue)
plot(upper, "Upper Band", color=color.red)
plot(lower, "Lower Band", color=color.red)
""",
            "generation": 1,
            "score": 0.92,
            "return_rate": 15.5,
            "sharpe_ratio": 1.8,
            "max_drawdown": -12.3,
            "win_rate": 0.65,
            "trades": 42
        }
        
        # 保存策略
        strategy_id = db_manager.save_strategy(example_strategy)
        logger.info(f"示例策略保存成功，ID: {strategy_id}")
        
        return strategy_id
    
    except Exception as e:
        logger.error(f"保存示例策略失敗: {str(e)}")
        raise

def main():
    """主程序"""
    try:
        # 初始化數據庫
        db_manager = init_database()
        
        # 保存示例策略
        strategy_id = save_example_strategy(db_manager)
        
        # 獲取並顯示保存的策略
        strategies = db_manager.get_top_strategies(limit=5)
        logger.info("\n最佳策略列表:")
        for strategy in strategies:
            logger.info(f"""
策略 ID: {strategy.id}
代數: {strategy.generation}
評分: {strategy.score}
收益率: {strategy.return_rate}%
夏普比率: {strategy.sharpe_ratio}
最大回撤: {strategy.max_drawdown}%
勝率: {strategy.win_rate}
交易次數: {strategy.trades}
            """)
            
    except Exception as e:
        logger.error(f"程序執行失敗: {str(e)}")
        raise

if __name__ == "__main__":
    main() 