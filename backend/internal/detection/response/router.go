package response

import (
	"github.com/gofiber/fiber/v2"
)

type responseHandler interface {
	FindOneByQueryId(ctx *fiber.Ctx) error
}

func SetupResponseRoutes(app *fiber.App, h responseHandler) {
	g := app.Group("/api/detection")

	g.Get("/result/:id", h.FindOneByQueryId)
}
