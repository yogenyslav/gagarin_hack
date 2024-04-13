package server

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"gagarin/config"
	"gagarin/internal/detection/query"
	"gagarin/internal/detection/response"
	servresp "gagarin/internal/server/response"
	"gagarin/pkg/storage/minios3"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	loggermw "github.com/gofiber/fiber/v2/middleware/logger"
	recovermw "github.com/gofiber/fiber/v2/middleware/recover"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/yogenyslav/logger"
	"github.com/yogenyslav/storage/postgres"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Server struct {
	cfg *config.Config
	app *fiber.App
	pg  *pgxpool.Pool
}

func New(cfg *config.Config) *Server {
	app := fiber.New(fiber.Config{
		ServerHeader: "Fiber",
		BodyLimit:    1024 * 1024 * 1024,
		ErrorHandler: servresp.ErrorHandler,
		AppName:      "Gagarin API",
	})
	app.Use(loggermw.New())
	app.Use(recovermw.New())
	app.Use(cors.New(cors.Config{
		AllowOrigins:     cfg.Server.CorsOrigins,
		AllowHeaders:     "",
		AllowCredentials: false,
	}))

	pg := postgres.MustNew(&cfg.Postgres, 20)

	return &Server{
		cfg: cfg,
		app: app,
		pg:  pg,
	}
}

func (s *Server) Run() {
	s3 := minios3.MustNew(&s.cfg.S3)
	if buckets, err := s3.ListBuckets(context.Background()); err != nil || len(buckets) == 0 {
		if err = s3.CreateBuckets(context.Background()); err != nil {
			logger.Panicf("failed to create s3 buckets: %v", err)
		}
	}

	var grpcOpts []grpc.DialOption
	grpcOpts = append(grpcOpts, grpc.WithTransportCredentials(insecure.NewCredentials()))
	mlAddr := fmt.Sprintf("%s:%d", s.cfg.Ml.Host, s.cfg.Ml.Port)
	mlConn, err := grpc.Dial(mlAddr, grpcOpts...)
	if err != nil {
		logger.Panicf("failed to connect to ml service: %v", err)
	}

	responseRepo := response.NewRepo(s.pg)
	responseController := response.NewController(responseRepo, mlConn)
	responseHandler := response.NewHandler(responseController)
	response.SetupResponseRoutes(s.app, responseHandler)

	queryRepo := query.NewRepo(s.pg)
	queryController := query.NewController(queryRepo, responseController, mlConn, s3)
	queryHandler := query.NewHandler(queryController)
	query.SetupQueryRoutes(s.app, queryHandler)

	go s.listen(&s.cfg.Server)

	ch := make(chan os.Signal, 1)
	signal.Notify(ch, syscall.SIGTERM, syscall.SIGINT)
	<-ch

	s.pg.Close()
	queryController.CancelProcessing()
	if err = s.app.Shutdown(); err != nil {
		logger.Warnf("failed to shutdown the app: %v", err)
	}
	if err = mlConn.Close(); err != nil {
		logger.Warnf("failed to close grpc conn: %v", err)
	}
	logger.Info("app was gracefully shutdown")
	os.Exit(0)
}

func (s *Server) listen(cfg *config.ServerConfig) {
	if err := s.app.Listen(fmt.Sprintf(":%d", cfg.Port)); err != nil {
		logger.Errorf("unexpectedly stopping the server: %v", err)
	}
}
