# Docker Troubleshooting Guide

## Common Issues and Solutions

### Issue: Postgres Service Exits with Code 1

**Error Message:**
```
psql:/docker-entrypoint-initdb.d/init.sql: error: could not read from input file: Is a directory
```

**Cause:** The `docker/postgres/init.sql` path is a directory instead of a file.

**Solution:**
1. Delete the directory:
   ```powershell
   Remove-Item -Path "docker\postgres\init.sql" -Recurse -Force
   ```

2. Create the file `docker/postgres/init.sql` with content:
   ```sql
   -- PostgreSQL initialization script for Airflow database
   -- The database 'airflow' is already created by POSTGRES_DB environment variable
   ```

3. Restart services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Issue: Airflow Cannot Connect to Postgres

**Error Message:**
```
psycopg2.OperationalError: could not translate host name "postgres" to address: Name or service not known
```

**Causes:**
1. Postgres service is not running
2. Postgres service exited before Airflow started
3. Network connectivity issues

**Solutions:**

1. **Check if postgres is running:**
   ```bash
   docker-compose ps postgres
   ```
   Should show status as "Up (healthy)"

2. **Check postgres logs:**
   ```bash
   docker-compose logs postgres
   ```

3. **Ensure postgres starts before Airflow:**
   - The `depends_on` with `condition: service_healthy` should handle this
   - If issues persist, restart in order:
     ```bash
     docker-compose up -d postgres
     # Wait for postgres to be healthy
     docker-compose up -d warehouse
     # Wait for warehouse to be healthy
     docker-compose up -d airflow
     ```

4. **Verify network connectivity:**
   ```bash
   docker-compose exec airflow ping postgres
   ```

### Issue: Airflow Entrypoint Script Fails

**Error:** Entrypoint script exits before Airflow starts

**Solution:** The entrypoint script has been updated with better retry logic:
- Maximum retry attempts (30)
- Better error messages
- Proper exit codes

If you need to update the entrypoint:
```bash
# Edit airflow-entrypoint.sh
# Then restart airflow
docker-compose restart airflow
```

### Issue: Atlas Service Unhealthy

**Status:** Shows as "unhealthy" in `docker-compose ps`

**Note:** Atlas may take several minutes to fully start. The health check may fail initially but the service can still be functional.

**Check Atlas:**
```bash
curl http://localhost:21000/api/atlas/admin/version
```

If it returns a version, Atlas is working despite the health check status.

### Issue: Port Conflicts

**Error:** Port already in use

**Solutions:**
1. Check what's using the port:
   ```bash
   # Windows
   netstat -ano | findstr :8080
   
   # Or check Docker
   docker ps | findstr 8080
   ```

2. Change ports in `docker-compose.yml` if needed

3. Stop conflicting services

### Issue: Volume Mount Errors

**Error:** Cannot mount volume or file not found

**Solutions:**
1. Ensure all paths in `docker-compose.yml` are correct
2. Use absolute paths or paths relative to docker-compose.yml location
3. Check file permissions (especially on Windows with WSL)

### Issue: Airflow DB Initialization Fails

**Error:** `airflow db init` fails

**Solutions:**
1. Ensure postgres is healthy:
   ```bash
   docker-compose ps postgres
   ```

2. Check Airflow can connect:
   ```bash
   docker-compose exec airflow airflow db check
   ```

3. Manually initialize if needed:
   ```bash
   docker-compose exec airflow airflow db init
   ```

### General Troubleshooting Steps

1. **Check all service status:**
   ```bash
   docker-compose ps
   ```

2. **View logs for specific service:**
   ```bash
   docker-compose logs <service-name>
   # Example:
   docker-compose logs airflow
   docker-compose logs postgres
   ```

3. **Restart a specific service:**
   ```bash
   docker-compose restart <service-name>
   ```

4. **Rebuild and restart everything:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

5. **Check Docker network:**
   ```bash
   docker network ls
   docker network inspect <network-name>
   ```

6. **Verify service dependencies:**
   ```bash
   docker-compose config
   ```

### Service Startup Order

The correct startup order (handled automatically by `depends_on`):
1. `postgres` - Airflow database (must be healthy)
2. `warehouse` - Warehouse database (must be healthy)
3. `atlas` - Depends on warehouse
4. `airflow` - Depends on postgres and warehouse

### Health Check Verification

Verify health checks are working:
```bash
# Check postgres health
docker-compose exec postgres pg_isready -U airflow

# Check warehouse health
docker-compose exec warehouse pg_isready -U warehouse

# Check Atlas (may take time)
curl http://localhost:21000/api/atlas/admin/version
```

### Clean Restart

If all else fails, do a clean restart:
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove the problematic directory if it exists
Remove-Item -Path "docker\postgres\init.sql" -Recurse -Force -ErrorAction SilentlyContinue

# Recreate the init.sql file
# (See solution above)

# Start fresh
docker-compose up -d
```

### Getting Help

If issues persist:
1. Check all service logs: `docker-compose logs`
2. Verify docker-compose.yml syntax: `docker-compose config`
3. Check Docker daemon is running
4. Verify sufficient resources (memory, disk space)


