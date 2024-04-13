package pkg

import (
	"errors"
	"net/http"

	"gagarin/internal/shared"

	"github.com/gofiber/fiber/v2"
	"github.com/jackc/pgx/v5/pgconn"
)

func CheckDuplicateKey(err error) bool {
	var pgError *pgconn.PgError
	return errors.As(err, &pgError) && pgError.Code == shared.UniqueViolationCode
}

func CheckPageNotFound(err error) bool {
	var fiberError *fiber.Error
	return errors.As(err, &fiberError) && fiberError.Code == http.StatusNotFound
}
