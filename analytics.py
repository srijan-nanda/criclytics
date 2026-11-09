import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "player", "team", "matches", "innings", "runs",
    "balls_faced", "fours", "sixes", "not_outs",
    "wickets", "balls_bowled", "runs_conceded"
]

INTEGER_COLUMNS = REQUIRED_COLUMNS[2:]


def load_data(file):
    """Load cricket statistics and reject incomplete or inconsistent records."""
    try:
        df = pd.read_csv(file)
    except pd.errors.EmptyDataError as error:
        raise ValueError("The CSV file is empty.") from error
    except (pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError("The uploaded file is not a valid readable CSV.") from error

    if df.empty:
        raise ValueError("The CSV file contains no player records.")

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

    df = df[REQUIRED_COLUMNS].copy()

    for column in ("player", "team"):
        df[column] = df[column].astype("string").str.strip()
        if df[column].isna().any() or df[column].eq("").any():
            raise ValueError(f"The '{column}' column cannot contain blank values.")

    duplicate_players = df["player"].str.casefold().duplicated(keep=False)
    if duplicate_players.any():
        names = sorted(df.loc[duplicate_players, "player"].unique().tolist())
        raise ValueError(
            "Each player must have one aggregated record. Duplicate players: "
            + ", ".join(names)
        )

    for column in INTEGER_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df[INTEGER_COLUMNS].isna().any().any():
        raise ValueError("Numeric columns contain missing or invalid values.")

    values = df[INTEGER_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Numeric columns must contain finite values.")

    if (df[INTEGER_COLUMNS] < 0).any().any():
        raise ValueError("Statistics cannot contain negative values.")

    non_integer = (df[INTEGER_COLUMNS] % 1 != 0).any().any()
    if non_integer:
        raise ValueError("Match and performance count columns must contain whole numbers.")

    if (df["innings"] > df["matches"]).any():
        raise ValueError("Innings cannot exceed matches.")

    if (df["not_outs"] > df["innings"]).any():
        raise ValueError("Not-outs cannot exceed innings.")

    if ((df["fours"] * 4 + df["sixes"] * 6) > df["runs"]).any():
        raise ValueError("Boundary runs cannot exceed total runs.")

    if ((df["fours"] + df["sixes"]) > df["balls_faced"]).any():
        raise ValueError("The number of boundaries cannot exceed balls faced.")

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

    result["boundary_runs"] = result["fours"] * 4 + result["sixes"] * 6

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


def _validate_limit(limit):
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be a positive integer.")


def top_batters(df, limit=5):
    """Return the highest run scorers."""
    _validate_limit(limit)
    return df.sort_values("runs", ascending=False).head(limit)


def top_bowlers(df, limit=5):
    """Return the highest wicket takers."""
    _validate_limit(limit)
    return df[df["wickets"] > 0].sort_values(
        "wickets", ascending=False
    ).head(limit)


def compare_players(df, player_names):
    """Return selected players, rejecting empty, duplicate or unknown names."""
    names = list(player_names)

    if not names:
        raise ValueError("Select at least one player to compare.")

    if len(names) != len(set(names)):
        raise ValueError("A player can only be selected once.")

    selected = df[df["player"].isin(names)]

    if selected["player"].nunique() != len(names):
        raise ValueError("One or more selected players were not found.")

    return selected
