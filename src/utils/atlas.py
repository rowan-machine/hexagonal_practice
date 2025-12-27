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
            # Atlas v2 API: Use bulk endpoint for publishing entities
            # Sort entities by type to ensure dependencies are created first:
            # 1. hive_db (databases)
            # 2. hive_table (tables - depend on databases)
            # 3. Process (processes - depend on tables)
            entity_count = len(payload.get("entities", []))
            self.log_info(f"Publishing to Atlas", entity_count=entity_count)
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            entities = payload.get("entities", [])
            type_order = {"hive_db": 1, "hive_table": 2, "Process": 3}
            
            # Group entities by type to publish in dependency order
            entities_by_type = {}
            for entity in entities:
                entity_type = entity.get("typeName", "")
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append(entity)
            
            # Publish in dependency order: databases first, then tables, then processes
            url = f"{self.base_url}/api/atlas/v2/entity/bulk"
            published_count = 0
            
            for entity_type in ["hive_db", "hive_table", "Process"]:
                if entity_type not in entities_by_type:
                    continue
                
                type_entities = entities_by_type[entity_type]
                bulk_payload = {"entities": type_entities}
                
                try:
                    # Try without auth first
                    response = requests.post(
                        url,
                        json=bulk_payload,
                        timeout=30,
                        headers=headers
                    )
                    
                    # Check for authentication errors
                    if response.status_code == 401:
                        # Try with default credentials (admin/admin)
                        self.log_info("Atlas requires authentication, retrying with admin/admin")
                        response = requests.post(
                            url,
                            json=bulk_payload,
                            timeout=30,
                            headers=headers,
                            auth=("admin", "admin")
                        )
                    
                    if response.status_code == 200:
                        published_count += len(type_entities)
                        self.log_info(f"Published {len(type_entities)} {entity_type} entities")
                    else:
                        # Log error but continue
                        error_text = response.text[:500] if response.text else "Unknown error"
                        self.log_warning(
                            f"Failed to publish {entity_type} entities",
                            status_code=response.status_code,
                            response_text=error_text
                        )
                        
                except requests.exceptions.RequestException as e:
                    self.log_warning(
                        f"Error publishing {entity_type} entities",
                        error=str(e)
                    )
            
            if published_count > 0:
                self.log_info(f"Atlas metadata published successfully", entity_count=published_count)
            else:
                self.log_warning("No entities were published to Atlas")
            
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
