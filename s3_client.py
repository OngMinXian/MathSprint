import boto3
import pandas as pd
from cachetools import cached, TTLCache

s3_client = boto3.client('s3')

@cached(cache=TTLCache(maxsize=5, ttl=int(60)))
def get_scoreboard_from_s3() -> pd.DataFrame:
    """
    Retrieves scoreboard csv from S3 and reads it into a Pandas DataFrame.
    The function is cached to reduce repeated get operations in a short timeframe.
    """
    scoreboard = s3_client.get_object(Bucket='mathsprint', Key='mathsprint_scoreboard.csv')['Body']
    df_scoreboard = pd.read_csv(scoreboard)
    return df_scoreboard

def write_scoreboard_to_s3(df_scoreboard: pd.DataFrame) -> None:
    """
    Writes a Pandas DataFrame to scoreboard csv in S3.
    """
    df_scoreboard.to_csv('mathsprint_scoreboard.csv', index=False)
    s3_client.upload_file(Filename = 'mathsprint_scoreboard.csv', Bucket= 'mathsprint', Key = 'mathsprint_scoreboard.csv')
