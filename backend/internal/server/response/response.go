package response

import (
	"errors"
	"log/slog"
	"net/http"

	"gagarin/pkg"

	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
)

type ErrorResponse struct {
	Msg    string `json:"msg"`
	Status int    `json:"-"`
}

func ErrorHandler(ctx *fiber.Ctx, err error) error {
	e := handleError(err)
	slog.Error(err.Error())
	return ctx.Status(e.Status).JSON(e)
}

func handleError(err error) ErrorResponse {
	var (
		ok               bool
		e                ErrorResponse
		validationErrors validator.ValidationErrors
	)

	if pkg.CheckPageNotFound(err) {
		return ErrorResponse{
			Msg:    "page not found",
			Status: http.StatusNotFound,
		}
	}

	if errors.As(err, &validationErrors) {
		return ErrorResponse{
			Msg:    err.Error(),
			Status: http.StatusUnprocessableEntity,
		}
	}

	e, ok = errStatus[err]
	if !ok {
		e = ErrorResponse{
			Msg:    err.Error(),
			Status: http.StatusInternalServerError,
		}
	}
	if e.Msg == "" {
		e.Msg = err.Error()
	}

	return e
}
