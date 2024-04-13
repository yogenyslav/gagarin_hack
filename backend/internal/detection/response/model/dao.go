package model

import (
	"time"

	"gagarin/internal/shared"
)

type Response struct {
	QueryId   int64                 `db:"query_id"`
	Status    shared.ResponseStatus `db:"status"`
	CreatedAt time.Time             `json:"created_at"`
	UpdatedAt time.Time             `json:"updated_at"`
}

type ResultResponse struct {
	Type    shared.QueryType      `db:"type"`
	QueryId int64                 `db:"query_id"`
	Status  shared.ResponseStatus `db:"status"`
}
