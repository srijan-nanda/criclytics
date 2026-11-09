import pytest

from analytics import (
    load_data,
    calculate_metrics,
    top_batters,
    top_bowlers,
    compare_players
)

DATA_PATH = "data/cricket_stats.csv"


def test_dataset_loads():
    df = load_data(DATA_PATH)
    assert len(df) == 8


def test_batting_average():
    df = calculate_metrics(load_data(DATA_PATH))
    virat = df[df["player"] == "Virat Sharma"].iloc[0]
    assert virat["batting_average"] == pytest.approx(69.29, abs=0.01)


def test_strike_rate():
    df = calculate_metrics(load_data(DATA_PATH))
    virat = df[df["player"] == "Virat Sharma"].iloc[0]
    assert virat["strike_rate"] == pytest.approx(151.56, abs=0.01)


def test_boundary_percentage():
    df = calculate_metrics(load_data(DATA_PATH))
    virat = df[df["player"] == "Virat Sharma"].iloc[0]
    assert virat["boundary_percentage"] == pytest.approx(61.86, abs=0.01)


def test_bowling_economy():
    df = calculate_metrics(load_data(DATA_PATH))
    arjun = df[df["player"] == "Arjun Singh"].iloc[0]
    assert arjun["economy"] == pytest.approx(6.45, abs=0.01)


def test_top_batter():
    df = calculate_metrics(load_data(DATA_PATH))
    assert top_batters(df, 1).iloc[0]["player"] == "Virat Sharma"


def test_top_bowler():
    df = calculate_metrics(load_data(DATA_PATH))
    assert top_bowlers(df, 1).iloc[0]["player"] == "Karan Das"


def test_player_comparison():
    df = calculate_metrics(load_data(DATA_PATH))
    result = compare_players(df, ["Virat Sharma", "Arjun Singh"])
    assert len(result) == 2


def test_invalid_player():
    df = calculate_metrics(load_data(DATA_PATH))
    with pytest.raises(ValueError):
        compare_players(df, ["Unknown Player"])


def test_negative_statistics_rejected(tmp_path):
    import pandas as pd

    df = pd.read_csv(DATA_PATH)
    df.loc[0, "runs"] = -10

    file = tmp_path / "invalid.csv"
    df.to_csv(file, index=False)

    with pytest.raises(ValueError):
        load_data(file)
