"""test_stats.py —— 统计核心逻辑单元测试（纯逻辑，无需 FastAPI）。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stats


def test_wilson_lower_zero_n():
    assert stats.wilson_lower(0, 0) == 0.0


def test_wilson_lower_valid_range():
    # 胜率下界应介于 0 和 1 之间，且低于纯胜率
    w = stats.wilson_lower(6, 10)  # 60%
    assert 0 < w < 0.6
    assert stats.wilson_lower(6, 10) < stats.wilson_lower(60, 100)  # 样本越大下界越高


def test_wilson_lower_more_games_higher():
    # 同胜率，样本越多下界越高（体现场次影响）
    vals = [stats.wilson_lower(int(0.6*n), n) for n in range(10, 201, 10)]
    assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))  # 单调递增


def test_shrink_pulls_toward_prior():
    # 收缩+下界：小样本(5场100%)得分应明显低（被压向平均/置信下界）
    s = stats.shrink(5, 5, 0.5)
    assert 0.0 < s < 0.6  # 不再是 100%，被压得很低
    assert s == stats.wilson_lower(5 + 25*0.5, 5 + 25)  # = posterior-wilson


def test_shrink_max_games_approaches_prior_zone():
    # 大样本收缩后接近原始胜率（先验影响小）
    s = stats.shrink(509, 1000, 0.5)
    assert abs(s - stats.wilson_lower(509, 1000)) < 0.01


def test_shrink_more_games_closer_to_prior_is_higher():
    # 越大样本 score 越高（同胜率）
    small = stats.shrink(5, 5, 0.5)
    big = stats.shrink(323, 634, 0.5)
    # 收缩+Wilson 下界：634 场的 50.9% 应高于 5 场的 100%（样本权重）
    assert big > small
