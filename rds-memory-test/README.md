# RDS Memory Test

This project tests memory consumption of MySQL and PostgreSQL databases with different memory limits using Docker containers.

## Structure
- `docker-compose.yml` - 512MB memory limit
- `docker-compose-1gb.yml` - 1GB memory limit  
- `docker-compose-2gb.yml` - 2GB memory limit
- `init-mysql.sql` - MySQL table schema
- `init-postgres.sql` - PostgreSQL table schema
- `generate_data.py` - Data generation script
- `monitor_memory.py` - Memory monitoring script

## Usage
1. Start containers: `docker-compose up -d`
2. Generate data: `python generate_data.py`
3. Monitor memory: `python monitor_memory.py`
4. Stop containers: `docker-compose down`

## Test Data Schema
- record_id: BIGINT (int8)
- uuid_text: VARCHAR(36) (text)
- category: INT (int4, values 1-4)
- timestamp_col: DATETIME/TIMESTAMP
