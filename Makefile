include .env

.PHONY: docker_up
docker_up:
	docker compose up -d --build

.PHONY: docker_down
docker_down:
	docker compose down

.PHONY: docker_remove
docker_remove: docker_down
	docker volume rm ${PROJECT_DIR}_pg_data
	docker volume rm ${PROJECT_DIR}_mongo
	docker volume rm ${PROJECT_DIR}_mongo_conf
	docker volume rm ${PROJECT_DIR}_minio
	docker image rm ${PROJECT_DIR}_backend
	docker image rm ${PROJECT_DIR}_ml

.PHONY: docker_restart
docker_restart: docker_down docker_up

.PHONY: docker_purge_restart
docker_purge_restart: docker_remove docker_up

.PHONY: local
local:
	docker compose up pg ml mongo minio -d --build
	go run cmd/server/main.go

.PHONY: migrate_up
migrate_up:
	cd backend/migrations && goose postgres "user=${POSTGRES_USER} \
		password=${POSTGRES_PASSWORD} dbname=${POSTGRES_DB} sslmode=disable \
		host=${POSTGRES_HOST} port=${POSTGRES_PORT}" up

.PHONY: migrate_down
migrate_down:
	cd backend/migrations && goose postgres "user=${POSTGRES_USER} \
		password=${POSTGRES_PASSWORD} dbname=${POSTGRES_DB} sslmode=disable \
		host=localhost port=${POSTGRES_PORT}" down

.PHONY: migrate_new
migrate_new:
	cd backend/migrations && goose postgres "user=${POSTGRES_USER} \
		password=${POSTGRES_PASSWORD} dbname=${POSTGRES_DB} sslmode=disable \
		host=localhost port=${POSTGRES_PORT}" create $(name) sql

proto_py:
	python -m grpc_tools.protoc -Iprotos --python_out=ml/pb --pyi_out=ml/pb --grpc_python_out=ml/pb protos/detection.proto

.PHONY: proto_go
proto_go:
	protoc --go_out=$(dest) --go_opt=Mprotos/detection.proto=internal/pb \
		--go-grpc_out=$(dest) --go-grpc_opt=Mprotos/detection.proto=internal/pb \
		protos/detection.proto
