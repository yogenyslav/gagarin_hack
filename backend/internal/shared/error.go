package shared

import (
	"errors"
)

// 400
var (
	ErrWrongQueryType      = errors.New("unable to match query type")
	ErrWrongResponseStatus = errors.New("unable to match response status")
	ErrWrongAnomalyClass   = errors.New("unable to match anomaly class")
	ErrQueryIsNotProcessed = errors.New("query with this id is not being processed")
)

// 500
var (
	ErrInsertRecord = errors.New("failed to insert record")
	ErrFindRecord   = errors.New("failed to find record")
	ErrUpdateRecord = errors.New("failed to update record")
	ErrProcessQuery = errors.New("error while processing query")
	ErrFindResult   = errors.New("failed to find result of processed query")
)
