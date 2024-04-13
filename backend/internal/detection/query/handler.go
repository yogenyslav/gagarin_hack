package query

import (
	"context"
	"net/http"
	"strconv"
	"strings"

	"gagarin/internal/detection/query/model"
	"gagarin/internal/shared"

	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
	"github.com/klauspost/compress/zip"
	"github.com/yogenyslav/logger"
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

	rawFile, err := ctx.FormFile("source")
	if err != nil {
		return err
	}

	file, err := rawFile.Open()
	if err != nil {
		return err
	}
	defer file.Close()

	m := ctx.FormValue("model")
	modelType, err := shared.ModelTypeFromString(m)
	if err != nil {
		return err
	}

	req := model.QueryCreate{
		Type:  shared.VideoType,
		Video: file,
		Model: modelType,
		Name:  rawFile.Filename,
		Size:  rawFile.Size,
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

	if !strings.HasPrefix(req.Source, "rtsp://") {
		return shared.ErrStreamLinkInvalid
	}

	m := req.Model
	modelType, err := shared.ModelTypeFromString(m)
	if err != nil {
		return err
	}

	queryCreate := model.QueryCreate{
		Source: req.Source,
		Type:   shared.StreamType,
		Model:  modelType,
	}
	queryId, err = h.controller.InsertOne(ctx.Context(), queryCreate)
	if err != nil {
		return err
	}

	return ctx.Status(http.StatusCreated).JSON(model.QueryResponse{
		Id: queryId,
	})
}

func (h *Handler) Archive(ctx *fiber.Ctx) error {
	var (
		err     error
		queryId int64
	)

	rawArchive, err := ctx.FormFile("source")
	if err != nil {
		return err
	}

	m := ctx.FormValue("model")
	modelType, err := shared.ModelTypeFromString(m)
	if err != nil {
		return err
	}

	a, err := rawArchive.Open()
	if err != nil {
		return err
	}
	defer a.Close()

	archive, err := zip.NewReader(a, rawArchive.Size)
	if err != nil {
		return err
	}

	resp := model.QueryArchiveResponse{
		Ids: make([]int64, 0),
	}
	for _, file := range archive.File {
		if file.FileInfo().IsDir() {
			logger.Debugf("skipping directory %s", file.FileInfo().Name())
			continue
		}

		logger.Debugf("processing file %s", file.FileInfo().Name())

		f, err := file.Open()
		if err != nil {
			return err
		}

		req := model.QueryCreate{
			Type:  shared.VideoType,
			Video: f,
			Model: modelType,
			Name:  file.FileInfo().Name(),
			Size:  file.FileInfo().Size(),
		}
		queryId, err = h.controller.InsertOne(ctx.Context(), req)
		if err != nil {
			return err
		}

		resp.Ids = append(resp.Ids, queryId)
	}

	return ctx.Status(http.StatusCreated).JSON(resp)
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
