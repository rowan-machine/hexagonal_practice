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
            # Atlas v2 API uses /api/atlas/v2/entity/bulk for batch operations
            # But single entity endpoint is /api/atlas/v2/entity
            url = f"{self.base_url}/api/atlas/v2/entity"
            entity_count = len(payload.get("entities", []))
            self.log_info(f"Publishing to Atlas", url=url, entity_count=entity_count)
            
            # Try without auth first (some Atlas setups don't require it)
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=10,
                headers=headers
            )
            
            # Check for authentication errors
            if response.status_code == 401:
                # Try with default credentials (admin/admin)
                self.log_info("Atlas requires authentication, retrying with admin/admin")
                response = requests.post(
                    url,
                    json=payload,
                    timeout=10,
                    headers=headers,
                    auth=("admin", "admin")
                )
            
            # Log response details for debugging
            if response.status_code != 200:
                self.log_warning(
                    f"Atlas returned non-200 status",
                    status_code=response.status_code,
                    response_text=response.text[:200]
                )
            
            response.raise_for_status()
            
            self.log_info("Atlas metadata published successfully", entity_count=entity_count)
        except requests.exceptions.RequestException as e:
            # Don't fail the pipeline if Atlas publish fails - just log warning
            status_code = None
            response_text = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                response_text = e.response.text[:200] if e.response.text else None
            
            self.log_warning(
                f"Atlas publish failed (this is non-critical)",
                error=str(e),
                url=url,
                status_code=status_code,
                response_text=response_text
            )
        except Exception as e:
            self.log_error(f"Unexpected error publishing to Atlas", error=e, exc_info=True)
