from datetime import datetime, timedelta


class TimestampGenerator:

    def __init__(self, start_date: datetime, end_date: datetime, delta_time: int):
        """
        Initialize the timestamp generator with start and end dates.

        Args:
            start_date (datetime): Start date as a datetime object.
            end_date (datetime): End date as a datetime object.
            delta_time (int): Time delta in days between timestamps.
        """
        self.current_date = start_date
        self.end_date = end_date
        self.delta_time = delta_time

    def __call__(self):
        """
        Return the next date as a string in 'YYYY-MM-DD' format.

        Returns:
            str: The next date as a string, or None if the end date is exceeded.
        """
        if self.current_date <= self.end_date:
            result = self.current_date.strftime("%Y-%m-%d")
            self.current_date += timedelta(days=self.delta_time)
            return result
        return None
