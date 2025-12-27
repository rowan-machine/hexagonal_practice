"""
Apache Atlas client for data lineage and governance.

Publishes metadata about databases, tables, and ETL processes to Atlas.
"""
from typing import Dict, Any, Optional
import requests
from src.mixins.logging import LoggingMixin


class AtlasClient(LoggingMixin):
    """
    Client for publishing metadata to Apache Atlas.
    
    Handles publishing of data lineage, table schemas, and ETL process metadata.
    Can be disabled for local development or testing.
    
    Usage:
        ```python
        from src.utils.atlas import AtlasClient
        
        client = AtlasClient(base_url="http://atlas:21000", enabled=True)
        client.publish(payload)
        ```
    """
    
    def __init__(self, base_url: str, enabled: bool = True):
        """
        Initialize Atlas client.
        
        Args:
            base_url: Base URL for Atlas API (e.g., "http://atlas:21000")
            enabled: Whether to actually publish to Atlas (False for local dev)
        """
        LoggingMixin.__init__(self, logger_name=self.__class__.__name__)
        self.base_url = base_url.rstrip('/')
        self.enabled = enabled
    
    def publish(self, payload: Dict[str, Any]) -> None:
        """
        Publish metadata payload to Atlas.
        
        Args:
            payload: Atlas entity payload dictionary
            
        Example:
            ```python
            payload = {
                "entities": [
                    {
                        "typeName": "hive_table",
                        "attributes": {
                            "qualifiedName": "warehouse.fact_policies@postgres",
                            "name": "fact_policies"
                        }
                    }
                ]
            }
            client.publish(payload)
            ```
        """
        if not self.enabled:
            self.log_info("Atlas disabled, skipping publish")
            return
        
        try:
            url = f"{self.base_url}/api/atlas/v2/entity"
            self.log_info(f"Publishing to Atlas", url=url, entity_count=len(payload.get("entities", [])))
            
            response = requests.post(
                url,
                json=payload,
                timeout=5,
            )
            response.raise_for_status()
            
            self.log_info("Atlas metadata published successfully")
        except requests.exceptions.RequestException as e:
            self.log_warning(f"Atlas publish failed", error=str(e), url=url)
        except Exception as e:
            self.log_error(f"Unexpected error publishing to Atlas", error=e, exc_info=True)
