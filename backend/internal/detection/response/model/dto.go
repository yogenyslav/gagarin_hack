package model

import (
	"gagarin/internal/shared"
)

type QueryResponseCreate struct {
	QueryId int64
}

type QueryResponseUpdate struct {
	QueryId int64
	Status  shared.ResponseStatus
}

type Anomaly struct {
	Ts    int64    `json:"ts"`
	Links []string `json:"link"`
	Cls   string   `json:"class"`
}

type ResultResponseDto struct {
	Type      string    `json:"type"`
	Status    string    `json:"status"`
	Anomalies []Anomaly `json:"anomalies"`
}
