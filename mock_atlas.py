"""
Mock Apache Atlas server for local development and testing.

This mock server simulates the Atlas API endpoint to allow testing
of metadata publishing without requiring a full Atlas installation.

Usage:
    python mock_atlas.py

The server will:
- Listen on http://localhost:21000
- Accept POST requests to /api/atlas/v2/entity
- Print received payloads to console
- Return success responses

This is useful for:
- Testing Atlas payload generation
- Debugging metadata publishing
- Local development without Atlas infrastructure
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from typing import Dict, Any
from datetime import datetime


class MockAtlasHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for mock Atlas API.
    
    Simulates the /api/atlas/v2/entity endpoint.
    """
    
    def log_message(self, format: str, *args: Any) -> None:
        """Override to suppress default request logging."""
        # Only log errors, not every request
        pass
    
    def do_POST(self) -> None:
        """
        Handle POST requests to Atlas API endpoint.
        
        Accepts payloads at /api/atlas/v2/entity and prints them.
        """
        if self.path != "/api/atlas/v2/entity":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')
            return
        
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        # Print received payload
        print("\n" + "=" * 60)
        print(f"Atlas Payload Received - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        if not body:
            print("⚠️  Empty request body")
        else:
            try:
                payload = json.loads(body)
                entities = payload.get("entities", [])
                
                print(f"\n📦 Entities: {len(entities)}")
                
                for i, entity in enumerate(entities, 1):
                    entity_type = entity.get("typeName", "unknown")
                    attributes = entity.get("attributes", {})
                    name = attributes.get("name", "unnamed")
                    qualified_name = attributes.get("qualifiedName", "unknown")
                    
                    print(f"\n  Entity {i}:")
                    print(f"    Type: {entity_type}")
                    print(f"    Name: {name}")
                    print(f"    Qualified Name: {qualified_name}")
                    
                    # Show inputs/outputs for processes
                    if entity_type == "Process":
                        inputs = attributes.get("inputs", [])
                        outputs = attributes.get("outputs", [])
                        if inputs:
                            print(f"    Inputs: {len(inputs)}")
                            for inp in inputs[:3]:  # Show first 3
                                qn = inp.get("uniqueAttributes", {}).get("qualifiedName", "unknown")
                                print(f"      - {qn}")
                        if outputs:
                            print(f"    Outputs: {len(outputs)}")
                            for out in outputs[:3]:  # Show first 3
                                qn = out.get("uniqueAttributes", {}).get("qualifiedName", "unknown")
                                print(f"      - {qn}")
                
                # Print full JSON for debugging
                print(f"\n📄 Full Payload JSON:")
                print(json.dumps(payload, indent=2))
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Invalid JSON payload: {e}")
                print("\nRaw body:")
                print(body.decode("utf-8", errors="ignore"))
            except Exception as e:
                print(f"⚠️  Error processing payload: {e}")
                print("\nRaw body:")
                print(body.decode("utf-8", errors="ignore")[:500])
        
        print("\n" + "=" * 60)
        
        # Send success response
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {
            "status": "OK",
            "message": "Payload received by mock Atlas server",
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_GET(self) -> None:
        """Handle GET requests - return server status."""
        if self.path == "/" or self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "status": "running",
                "service": "Mock Atlas Server",
                "endpoint": "/api/atlas/v2/entity",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()


def run_mock_atlas(host: str = "localhost", port: int = 21000) -> None:
    """
    Run the mock Atlas server.
    
    Args:
        host: Host to bind to (default: localhost)
        port: Port to listen on (default: 21000)
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, MockAtlasHandler)
    
    print("=" * 60)
    print("Mock Apache Atlas Server")
    print("=" * 60)
    print(f"Listening on http://{host}:{port}")
    print(f"Endpoint: http://{host}:{port}/api/atlas/v2/entity")
    print(f"Health check: http://{host}:{port}/health")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down mock Atlas server...")
        httpd.server_close()
        print("Server stopped.")


if __name__ == "__main__":
    run_mock_atlas()
