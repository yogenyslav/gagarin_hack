package model

import (
	"gagarin/internal/shared"
)

type Query struct {
	Id        int64            `db:"id"`
	Type      shared.QueryType `db:"type"`
	Source    string           `db:"source"`
	CreatedAt string           `db:"created_at"`
}
