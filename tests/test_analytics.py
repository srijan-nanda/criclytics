import pandas as pd
import pytest

from analytics import (
    load_data,
    calculate_metrics,
    top_batters,
    top_bowlers,
    compare_players
)

DATA_PATH = "data/cricket_stats.csv"


def _write_csv(tmp_path, df):
    path = tmp_path / "dataset.csv"
    df.to_csv(path, index=False)
    return path


def _valid_frame():
    return pd.read_csv(DATA_PATH)


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


def test_zero_balls_faced_produces_undefined_strike_rate():
    df = pd.DataFrame([{
        "player": "Zero Ball", "team": "Test", "matches": 1, "innings": 1,
        "runs": 0, "balls_faced": 0, "fours": 0, "sixes": 0,
        "not_outs": 1, "wickets": 0, "balls_bowled": 0, "runs_conceded": 0
    }])
    result = calculate_metrics(df)
    assert pd.isna(result.loc[0, "strike_rate"])
    assert pd.isna(result.loc[0, "batting_average"])
    assert pd.isna(result.loc[0, "economy"])


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
    with pytest.raises(ValueError, match="not been found"):
        compare_players(df, ["Unknown Player"])


def test_negative_statistics_rejected(tmp_path):
    df = _valid_frame()
    df.loc[0, "runs"] = -10
    with pytest.raises(ValueError, match="negative"):
        load_data(_write_csv(tmp_path, df))


def test_missing_required_column_rejected(tmp_path):
    df = _valid_frame().drop(columns=["team"])
    with pytest.raises(ValueError, match="Missing columns"):
        load_data(_write_csv(tmp_path, df))


def test_blank_player_name_rejected(tmp_path):
    df = _valid_frame()
    df.loc[0, "player"] = "  "
    with pytest.raises(ValueError, match="player"):
        load_data(_write_csv(tmp_path, df))


def test_blank_team_name_rejected(tmp_path):
    df = _valid_frame()
    df.loc[0, "team"] = ""
    with pytest.raises(ValueError, match="team"):
        load_data(_write_csv(tmp_path, df))


def test_duplicate_player_records_rejected(tmp_path):
    df = _valid_frame()
    df.loc[1, "player"] = df.loc[0, "player"].upper()
    with pytest.raises(ValueError, match="Duplicate players"):
        load_data(_write_csv(tmp_path, df))


def test_fractional_count_rejected(tmp_path):
    df = _valid_frame()
    df.loc[0, "runs"] = 12.5
    with pytest.raises(ValueError, match="whole numbers"):
        load_data(_write_csv(tmp_path, df))


def test_innings_cannot_exceed_matches(tmp_path):
    df = _valid_frame()
    df.loc[0, "innings"] = df.loc[0, "matches"] + 1
    with pytest.raises(ValueError, match="Innings cannot exceed"):
        load_data(_write_csv(tmp_path, df))


def test_not_outs_cannot_exceed_innings(tmp_path):
    df = _valid_frame()
    df.loc[0, "not_outs"] = df.loc[0, "innings"] + 1
    with pytest.raises(ValueError, match="Not-outs cannot exceed"):
        load_data(_write_csv(tmp_path, df))


def test_boundary_count_cannot_exceed_balls_faced(tmp_path):
    df = _valid_frame()
    df.loc[0, "fours"] = df.loc[0, "balls_faced"] + 1
    df.loc[0, "runs"] = max(df.loc[0, "runs"], df.loc[0, "fours"] * 4)
    with pytest.raises(ValueError, match="boundaries cannot exceed balls faced"):
        load_data(_write_csv(tmp_path, df))


def test_empty_csv_rejected(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")
    with pytest.raises(ValueError, match="empty"):
        load_data(path)


def test_empty_player_dataset_rejected(tmp_path):
    df = _valid_frame().iloc[0:0]
    with pytest.raises(ValueError, match="no player records"):
        load_data(_write_csv(tmp_path, df))


def test_top_batter_limit_must_be_positive():
    df = calculate_metrics(load_data(DATA_PATH))
    with pytest.raises(ValueError, match="positive integer"):
        top_batters(df, 0)


def test_top_bowler_limit_must_be_positive():
    df = calculate_metrics(load_data(DATA_PATH))
    with pytest.raises(ValueError, match="positive integer"):
        top_bowlers(df, -1)


def test_empty_player_comparison_rejected():
    df = calculate_metrics(load_data(DATA_PATH))
    with pytest.raises(ValueError, match="at least one player"):
        compare_players(df, [])


def test_duplicate_player_selection_rejected():
    df = calculate_metrics(load_data(DATA_PATH))
    with pytest.raises(ValueError, match="only be selected once"):
        compare_players(df, ["Virat Sharma", "Virat Sharma"])
