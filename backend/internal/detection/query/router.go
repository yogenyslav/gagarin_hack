package query

import (
	"github.com/gofiber/fiber/v2"
)

type queryHandler interface {
	Video(ctx *fiber.Ctx) error
	Stream(ctx *fiber.Ctx) error
	Archive(ctx *fiber.Ctx) error
	CancelById(ctx *fiber.Ctx) error
}

func SetupQueryRoutes(app *fiber.App, h queryHandler) {
	g := app.Group("/api/detection")

	g.Post("/video", h.Video)
	g.Post("/stream", h.Stream)
	g.Post("/archive", h.Archive)
	g.Post("/cancel/:id", h.CancelById)
}
