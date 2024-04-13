package response

import (
	"context"
	"net/http"
	"strconv"

	"gagarin/internal/detection/response/model"

	"github.com/gofiber/fiber/v2"
)

type responseController interface {
	FindOneByQueryId(ctx context.Context, queryId int64) (model.ResultResponseDto, error)
}

type Handler struct {
	controller responseController
}

func NewHandler(controller responseController) *Handler {
	return &Handler{
		controller: controller,
	}
}

func (h *Handler) FindOneByQueryId(ctx *fiber.Ctx) error {
	queryId, err := strconv.ParseInt(ctx.Params("id"), 10, 64)
	if err != nil {
		return err
	}

	resp, err := h.controller.FindOneByQueryId(ctx.Context(), queryId)
	if err != nil {
		return err
	}

	return ctx.Status(http.StatusOK).JSON(resp)
}
