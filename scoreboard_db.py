# Import libraries
import pandas as pd

def get_scoreboard() -> pd.DataFrame:
    """
    Reads scoreboard csv and returns pandas dataframe.
    """
    df_scoreboard = pd.read_csv('mathsprint_scoreboard.csv')
    return df_scoreboard

def write_scoreboard(df_scoreboard: pd.DataFrame) -> None:
    """
    Writes a Pandas DataFrame to scoreboard csv.
    """
    df_scoreboard.to_csv('mathsprint_scoreboard.csv', index=False)
