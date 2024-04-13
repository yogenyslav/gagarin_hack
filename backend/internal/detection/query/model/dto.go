package model

import (
	"io"

	"gagarin/internal/shared"
)

type StreamQueryReq struct {
	Source string `json:"source" validate:"required"`
	Model  string `json:"model" validate:"required"`
}

type QueryCreate struct {
	Source string
	Type   shared.QueryType
	Video  io.Reader
	Model  shared.ModelType
	Name   string
	Size   int64
}

type QueryResponse struct {
	Id int64 `json:"id"`
}

type QueryArchiveResponse struct {
	Ids []int64 `json:"ids"`
}

type ResultReq struct {
	Id int64 `json:"id" validate:"required,gte=1"`
}
