import pandas as pd

REQUIRED_COLUMNS = [
    "player", "team", "matches", "innings", "runs",
    "balls_faced", "fours", "sixes", "not_outs",
    "wickets", "balls_bowled", "runs_conceded"
]


def load_data(file):
    """Load and validate cricket statistics."""
    df = pd.read_csv(file)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

    numeric_columns = REQUIRED_COLUMNS[2:]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df[numeric_columns].isna().any().any():
        raise ValueError("Numeric columns contain missing or invalid values.")

    if (df[numeric_columns] < 0).any().any():
        raise ValueError("Statistics cannot contain negative values.")

    if (df["innings"] > df["matches"]).any():
        raise ValueError("Innings cannot exceed matches.")

    if (df["not_outs"] > df["innings"]).any():
        raise ValueError("Not-outs cannot exceed innings.")

    if ((df["fours"] * 4 + df["sixes"] * 6) > df["runs"]).any():
        raise ValueError("Boundary runs cannot exceed total runs.")

    return df


def calculate_metrics(df):
    """Calculate batting and bowling performance metrics."""
    result = df.copy()

    dismissals = result["innings"] - result["not_outs"]

    result["batting_average"] = (
        result["runs"] / dismissals.replace(0, float("nan"))
    )

    result["strike_rate"] = (
        result["runs"] / result["balls_faced"].replace(0, float("nan")) * 100
    )

    result["boundary_runs"] = (
        result["fours"] * 4 + result["sixes"] * 6
    )

    result["boundary_percentage"] = (
        result["boundary_runs"] / result["runs"].replace(0, float("nan")) * 100
    )

    result["economy"] = (
        result["runs_conceded"]
        / (result["balls_bowled"].replace(0, float("nan")) / 6)
    )

    result["bowling_average"] = (
        result["runs_conceded"] / result["wickets"].replace(0, float("nan"))
    )

    result["bowling_strike_rate"] = (
        result["balls_bowled"] / result["wickets"].replace(0, float("nan"))
    )

    return result.round(2)


def top_batters(df, limit=5):
    return df.sort_values(
        "runs", ascending=False
    ).head(limit)


def top_bowlers(df, limit=5):
    return df[df["wickets"] > 0].sort_values(
        "wickets", ascending=False
    ).head(limit)


def compare_players(df, player_names):
    selected = df[df["player"].isin(player_names)]

    if selected["player"].nunique() != len(set(player_names)):
        raise ValueError("One or more selected players were not found.")

    return selected
