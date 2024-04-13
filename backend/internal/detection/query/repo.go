package query

import (
	"context"

	"gagarin/internal/detection/query/model"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/yogenyslav/storage/postgres"
)

type Repo struct {
	pg *pgxpool.Pool
}

func NewRepo(pg *pgxpool.Pool) *Repo {
	return &Repo{
		pg: pg,
	}
}

const insertOne = `
	insert into query(type, source)
	values ($1, $2)
	returning id;
`

func (r *Repo) InsertOne(ctx context.Context, params model.Query) (int64, error) {
	return postgres.QueryPrimitive[int64](ctx, r.pg, insertOne, params.Type, params.Source)
}

const updateSource = `
	update query
	set source = $1
	where id = $2;
`

func (r *Repo) UpdateSource(ctx context.Context, id int64, source string) error {
	_, err := r.pg.Exec(ctx, updateSource, source, id)
	return err
}
