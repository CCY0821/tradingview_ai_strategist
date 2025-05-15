import pytest
from unittest.mock import patch
from core.strategy_generator import generate_strategy

@patch("core.strategy_generator._ask_gpt")
def test_generate_strategy(mock_ask):
    mock_ask.return_value = "//@version=5\nstrategy(...)"
    code = generate_strategy("測試")
    assert code.startswith("//@version=5")
