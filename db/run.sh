docker rm -f $(docker ps -a -q -f "name=navexa") || true
docker run -d \
  --name navexa \
  -e POSTGRES_USER=navexa_user \
  -e POSTGRES_PASSWORD=navexa_password \
  -e POSTGRES_DB=navexa_db \
  -v $(pwd)/create.sql:/docker-entrypoint-initdb.d/create.sql \
  -v $(pwd)/data.sql:/docker-entrypoint-initdb.d/data.sql \
  -p 5432:5432 \
  pgvector/pgvector:0.8.0-pg17

