"""CSV data reader with caching."""
import pandas as pd
from pathlib import Path
from typing import Optional


class CSVReader:
    """Loads and caches CSV registration data."""

    def __init__(self, csv_path: str):
        """
        Initialize CSV reader.

        Args:
            csv_path: Path to the CSV file

        Raises:
            FileNotFoundError: If CSV file doesn't exist
        """
        self.csv_path = Path(csv_path)
        self._dataframe: Optional[pd.DataFrame] = None

        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Load CSV immediately
        self._load_csv()

    def _load_csv(self) -> None:
        """Load CSV data into memory."""
        try:
            self._dataframe = pd.read_csv(
                self.csv_path,
                encoding='utf-8',
                dtype=str  # Keep all fields as strings
            )
            # Strip whitespace from all string columns
            self._dataframe = self._dataframe.apply(
                lambda x: x.str.strip() if x.dtype == "object" else x
            )
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}")

    def get_dataframe(self) -> pd.DataFrame:
        """
        Get the cached DataFrame.

        Returns:
            pandas DataFrame with registration data
        """
        if self._dataframe is None:
            self._load_csv()
        return self._dataframe.copy()  # Return a copy to prevent external modifications

    def reload(self) -> None:
        """Reload CSV data from disk."""
        self._load_csv()
