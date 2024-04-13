package response

import (
	"net/http"

	"gagarin/internal/shared"

	"github.com/gofiber/fiber/v2"
	"github.com/jackc/pgx/v5"
)

var errStatus = map[error]ErrorResponse{
	pgx.ErrNoRows: {
		Msg:    "no rows were found",
		Status: http.StatusNotFound,
	},
	fiber.ErrUnprocessableEntity: {
		Msg:    "data validation error",
		Status: http.StatusUnprocessableEntity,
	},

	// 400
	shared.ErrWrongResponseStatus: {
		Status: http.StatusBadRequest,
	},
	shared.ErrWrongAnomalyClass: {
		Status: http.StatusBadRequest,
	},
	shared.ErrWrongQueryType: {
		Status: http.StatusBadRequest,
	},
	shared.ErrQueryIsNotProcessed: {
		Status: http.StatusBadRequest,
	},

	// 500
	shared.ErrInsertRecord: {
		Status: http.StatusInternalServerError,
	},
	shared.ErrFindRecord: {
		Status: http.StatusInternalServerError,
	},
	shared.ErrUpdateRecord: {
		Status: http.StatusInternalServerError,
	},
	shared.ErrProcessQuery: {
		Status: http.StatusInternalServerError,
	},
	shared.ErrFindResult: {
		Status: http.StatusInternalServerError,
	},
}
