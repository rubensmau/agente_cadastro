"""Search functionality for registration data."""
import pandas as pd
from typing import List, Dict, Any


class RegistrationRecord:
    """Represents a single registration record with field filtering."""

    def __init__(self, raw_data: Dict[str, Any], exposed_fields: List[str]):
        """
        Initialize a registration record.

        Args:
            raw_data: Complete record data from CSV
            exposed_fields: List of fields that can be exposed to clients
        """
        self.raw_data = raw_data
        self.exposed_fields = exposed_fields

    def to_dict(self) -> Dict[str, Any]:
        """
        Return only exposed fields.

        Returns:
            Dictionary with only exposed fields
        """
        return {k: v for k, v in self.raw_data.items() if k in self.exposed_fields}


class RegistrationSearcher:
    """Search engine for registration data."""

    def __init__(self, dataframe: pd.DataFrame, exposed_fields: List[str]):
        """
        Initialize the searcher.

        Args:
            dataframe: Pandas DataFrame with registration data
            exposed_fields: List of fields to expose in results
        """
        self.df = dataframe
        self.exposed_fields = exposed_fields

    def search(self, query: Dict[str, str]) -> List[RegistrationRecord]:
        """
        Search for registration records matching the query.

        Performs case-insensitive partial matching on specified fields.

        Args:
            query: Dictionary of field:value pairs to search for
                   Example: {"name": "João", "city": "São Paulo"}

        Returns:
            List of RegistrationRecord objects matching the query
        """
        if not query:
            return []

        result_df = self.df.copy()

        # Apply filters for each query parameter
        for field, value in query.items():
            if field in result_df.columns and value:
                # Case-insensitive partial match
                result_df = result_df[
                    result_df[field].str.contains(
                        str(value), case=False, na=False, regex=False
                    )
                ]

        # Convert to RegistrationRecord objects
        records = [
            RegistrationRecord(row.to_dict(), self.exposed_fields)
            for _, row in result_df.iterrows()
        ]

        return records

    def search_exact(self, field: str, value: str) -> List[RegistrationRecord]:
        """
        Search for exact match on a specific field.

        Args:
            field: Field name to search in
            value: Exact value to match

        Returns:
            List of RegistrationRecord objects matching exactly
        """
        if field not in self.df.columns:
            return []

        result_df = self.df[self.df[field] == value]

        records = [
            RegistrationRecord(row.to_dict(), self.exposed_fields)
            for _, row in result_df.iterrows()
        ]

        return records
