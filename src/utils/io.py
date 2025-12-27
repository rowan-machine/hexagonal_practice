"""
I/O utilities for data access.

Encapsulates file and database operations to keep them out of domain logic.
"""
from typing import Any, List, Dict, Optional
from pathlib import Path
import json
from abc import ABC, abstractmethod
from src.mixins.logging import LoggingMixin


class DataReader(ABC, LoggingMixin):
    """Abstract base class for data readers."""
    
    def __init__(self, source: str, **kwargs):
        LoggingMixin.__init__(self, logger_name=f"{self.__class__.__name__}", **kwargs)
        self.source = source
    
    @abstractmethod
    def read(self) -> Any:
        """Read data from source."""
        pass


class FileReader(DataReader):
    """Reads data from files."""
    
    def __init__(self, source: str, file_format: str = "json", **kwargs):
        super().__init__(source, **kwargs)
        self.file_format = file_format
        self.path = Path(source)
    
    def read(self) -> Any:
        """Read data from file."""
        self.log_info(f"Reading file", path=str(self.path), format=self.file_format)
        
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        
        if self.file_format == "json":
            return self._read_json()
        elif self.file_format == "csv":
            return self._read_csv()
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")
    
    def _read_json(self) -> Any:
        """Read JSON file."""
        with open(self.path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _read_csv(self) -> List[Dict[str, Any]]:
        """Read CSV file."""
        import csv
        data = []
        with open(self.path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data


class DataWriter(ABC, LoggingMixin):
    """Abstract base class for data writers."""
    
    def __init__(self, destination: str, **kwargs):
        LoggingMixin.__init__(self, logger_name=f"{self.__class__.__name__}", **kwargs)
        self.destination = destination
    
    @abstractmethod
    def write(self, data: Any) -> None:
        """Write data to destination."""
        pass


class FileWriter(DataWriter):
    """Writes data to files."""
    
    def __init__(self, destination: str, file_format: str = "json", **kwargs):
        super().__init__(destination, **kwargs)
        self.file_format = file_format
        self.path = Path(destination)
    
    def write(self, data: Any) -> None:
        """Write data to file."""
        self.log_info(f"Writing file", path=str(self.path), format=self.file_format)
        
        # Ensure directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.file_format == "json":
            self._write_json(data)
        elif self.file_format == "csv":
            self._write_csv(data)
        else:
            raise ValueError(f"Unsupported file format: {self.file_format}")
    
    def _write_json(self, data: Any) -> None:
        """Write JSON file."""
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _write_csv(self, data: List[Dict[str, Any]]) -> None:
        """Write CSV file."""
        import csv
        if not data:
            return
        
        with open(self.path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


class DataAccessor:
    """
    Convenience class for data access operations.
    
    Wraps readers and writers to provide a simple interface.
    """
    
    def __init__(self, reader: Optional[DataReader] = None, writer: Optional[DataWriter] = None):
        self.reader = reader
        self.writer = writer
    
    def load(self) -> Any:
        """Load data using the configured reader."""
        if self.reader is None:
            raise ValueError("No reader configured")
        return self.reader.read()
    
    def save(self, data: Any) -> None:
        """Save data using the configured writer."""
        if self.writer is None:
            raise ValueError("No writer configured")
        self.writer.write(data)

