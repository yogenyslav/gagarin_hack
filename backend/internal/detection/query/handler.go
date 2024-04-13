package query

import (
	"context"
	"net/http"
	"strconv"

	"gagarin/internal/detection/query/model"
	"gagarin/internal/shared"

	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
)

type queryController interface {
	InsertOne(ctx context.Context, params model.QueryCreate) (int64, error)
	CancelById(ctx context.Context, id int64) error
}

type Handler struct {
	controller queryController
	validator  *validator.Validate
}

func NewHandler(controller queryController) *Handler {
	return &Handler{
		controller: controller,
		validator:  validator.New(validator.WithRequiredStructEnabled()),
	}
}

func (h *Handler) Video(ctx *fiber.Ctx) error {
	var (
		err     error
		queryId int64
	)

	file, err := ctx.FormFile("source")
	if err != nil {
		return err
	}

	req := model.QueryCreate{
		Type:  shared.VideoType,
		Video: file,
	}
	queryId, err = h.controller.InsertOne(ctx.Context(), req)
	if err != nil {
		return err
	}

	return ctx.Status(http.StatusCreated).JSON(model.QueryResponse{
		Id: queryId,
	})
}

func (h *Handler) Stream(ctx *fiber.Ctx) error {
	var (
		req     model.StreamQueryReq
		err     error
		queryId int64
	)

	if err = ctx.BodyParser(&req); err != nil {
		return err
	}
	if err = h.validator.Struct(&req); err != nil {
		return err
	}

	queryCreate := model.QueryCreate{
		Source: req.Source,
		Type:   shared.StreamType,
	}
	queryId, err = h.controller.InsertOne(ctx.Context(), queryCreate)
	if err != nil {
		return err
	}

	return ctx.Status(http.StatusCreated).JSON(model.QueryResponse{
		Id: queryId,
	})
}

func (h *Handler) CancelById(ctx *fiber.Ctx) error {
	id, err := strconv.ParseInt(ctx.Params("id"), 10, 64)
	if err != nil {
		return err
	}

	if err = h.controller.CancelById(ctx.Context(), id); err != nil {
		return err
	}

	return ctx.SendStatus(http.StatusNoContent)
}
