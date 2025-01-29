import argparse
import calendar
import json
import logging
import os
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import trafilatura
from tqdm import tqdm
import gdelt

warnings.filterwarnings('ignore')

def setup_logging(log_level):
    """Setup logging with console handler."""
    logger = logging.getLogger()
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    return logger

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Query GDELT API for person-specific news data.')

    parser.add_argument('--person', type=str, required=True, help='Person name to search for.')
    parser.add_argument('--start', type=str, required=True, help='Starting date as YYYY-MM.')
    parser.add_argument('--end', type=str, required=True, help='Ending date as YYYY-MM.')
    parser.add_argument('--query-column', type=str, default='V2Persons', help='Column to query (default: V2Persons).')
    parser.add_argument('--output-folder', type=str, default='data', help='Output file path.')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level.')

    args = parser.parse_args()
    args.start = datetime.strptime(args.start, "%Y-%m")
    args.end = datetime.strptime(args.end, "%Y-%m")

    return args

class GDeltAPI:
    """Class to interact with the GDELT API."""

    def __init__(self):
        self.api = gdelt.gdelt(version=2)

    def query_with_person(self, year, month, person, query_column='V2Persons', use_cols=None):
        """Query GDELT data for a specific person."""
        if use_cols is None:
            use_cols = [
                'DATE', 'SourceCommonName', 'DocumentIdentifier', 'V2Counts',
                'V2Themes', 'Locations', 'AllNames', 'V2Persons', 'Amounts', 'Extras'
            ]

        num_days = calendar.monthrange(year, month)[1]
        days = [datetime(year, month, day).strftime("%Y%m%d") for day in range(1, num_days + 1)]
        news_dfs_daily = []

        for day in tqdm(days, desc=f'Collecting articles for {year}-{month}'):
            try:
                news_df = self.api.Search([day], table='gkg')[use_cols]
                news_df = news_df.dropna(subset=[query_column])
                news_df[query_column] = news_df[query_column].str.lower().apply(
                    lambda x: x if person.lower() in x else np.nan
                )
                news_df = news_df.dropna()

                if not news_df.empty:
                    tqdm.write(f"Processing {len(news_df)} articles for {day}")
                    news_df = self.fetch_article_content(news_df)
                    news_dfs_daily.append(news_df)

            except Exception as exc:
                logging.error("Error processing day %s: %s", day, exc)

        if news_dfs_daily:
            final_df = pd.concat(news_dfs_daily)
            return final_df.dropna(subset=['article', 'comments'], how='all'), num_days

        return pd.DataFrame(), num_days

    @staticmethod
    def fetch_article_content(df):
        """Fetch article content using URLs."""
        article_texts, comments_list = [], []

        for url in tqdm(df['DocumentIdentifier'], desc="Fetching articles"):
            try:
                downloaded = trafilatura.fetch_url(url)
                content = trafilatura.extract(downloaded, output_format="json")
                content_json = json.loads(content) if content else {}
                article_texts.append(content_json.get('text'))
                comments_list.append(content_json.get('comments'))
            except Exception as exc:
                logging.error("Error fetching content for %s: %s", url, exc)
                article_texts.append(None)
                comments_list.append(None)

        df['article'] = article_texts
        df['comments'] = comments_list
        return df

def save_results(df, output_folder, file_name):
    """Save DataFrame to a CSV file."""
    os.makedirs(output_folder, exist_ok=True)
    file_path = Path(output_folder, file_name)
    df.to_csv(file_path, index=False)
    logging.info("Results saved to %s", file_path)

def main():
    """Main function to orchestrate the GDELT query process."""
    args = parse_arguments()
    setup_logging(getattr(logging, args.log_level))

    gdelt_api = GDeltAPI()

    current_date = args.start
    while current_date <= args.end:
        logging.info("Querying GDELT for %s in %s", args.person, current_date.strftime('%Y-%m'))

        results_df, num_days = gdelt_api.query_with_person(
            year=current_date.year,
            month=current_date.month,
            person=args.person,
            query_column=args.query_column
        )

        if not results_df.empty:
            save_results(results_df, args.output_folder, f"{args.person}_{current_date.strftime('%Y-%m')}.csv")
        else:
            logging.warning("No results found for %s", current_date.strftime('%Y-%m'))

        current_date += timedelta(days=num_days)

if __name__ == "__main__":
    main()
