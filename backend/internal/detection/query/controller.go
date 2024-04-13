package query

import (
	"context"
	"fmt"
	"strings"
	"sync"

	"gagarin/internal/detection/query/model"
	respmodel "gagarin/internal/detection/response/model"
	"gagarin/internal/pb"
	"gagarin/internal/shared"
	"gagarin/pkg"
	"gagarin/pkg/storage/minios3"

	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"github.com/yogenyslav/logger"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type queryRepo interface {
	InsertOne(ctx context.Context, params model.Query) (int64, error)
	UpdateSource(ctx context.Context, id int64, source string) error
}

type responseController interface {
	InsertOne(ctx context.Context, params respmodel.QueryResponseCreate) error
	UpdateOne(ctx context.Context, params respmodel.QueryResponseUpdate) error
}

type Controller struct {
	qr         queryRepo
	rc         responseController
	ml         pb.MlServiceClient
	s3         *minios3.S3
	processing map[int64]context.CancelFunc
	mu         sync.Mutex
}

func NewController(qr queryRepo, rc responseController, mlConn *grpc.ClientConn, s3 *minios3.S3) *Controller {
	return &Controller{
		qr:         qr,
		rc:         rc,
		ml:         pb.NewMlServiceClient(mlConn),
		s3:         s3,
		processing: make(map[int64]context.CancelFunc),
	}
}

func (ctrl *Controller) InsertOne(ctx context.Context, params model.QueryCreate) (int64, error) {
	var query model.Query

	if params.Type == shared.VideoType {
		rawFile, err := params.Video.Open()
		if err != nil {
			logger.Errorf("failed to open file: %v", err)
			return 0, err
		}

		split := strings.Split(params.Video.Filename, ".")
		source := fmt.Sprintf("%s%d.%s", uuid.NewString(), pkg.GetLocalTime().Unix(), split[len(split)-1])
		_, err = ctrl.s3.PutObject(ctx, shared.VideoBucket, source, rawFile, params.Video.Size, minio.PutObjectOptions{})
		if err != nil {
			logger.Errorf("failed to put file into s3: %v", err)
			return 0, shared.ErrInsertRecord
		}

		query.Source = source
	}

	id, err := ctrl.qr.InsertOne(ctx, query)
	if err != nil {
		logger.Errorf("failed to insert query: %v", err)
		return 0, shared.ErrInsertRecord
	}

	respCreate := respmodel.QueryResponseCreate{
		QueryId: id,
	}
	if err = ctrl.rc.InsertOne(ctx, respCreate); err != nil {
		return 0, err
	}

	go ctrl.process(context.Background(), id, query)

	return id, nil
}

func (ctrl *Controller) process(ctx context.Context, id int64, params model.Query) {
	withCancel, cancel := context.WithCancel(ctx)
	defer cancel()

	ctrl.mu.Lock()
	ctrl.processing[id] = cancel
	logger.Debugf("processing %v", ctrl.processing)
	ctrl.mu.Unlock()

	in := &pb.Query{
		Id:     id,
		Source: params.Source,
	}
	resp, err := ctrl.ml.Process(withCancel, in)
	if err != nil {
		grpcErr := status.Convert(err)
		if grpcErr.Code() != codes.Canceled {
			logger.Errorf("processing query %d failed: %v", id, err)
		}
	}

	logger.Infof("processing query %d finished with status %v", id, resp.GetStatus())

	s, err := shared.ResponseStatusFromString(resp.GetStatus().String())
	if err != nil {
		logger.Warnf("%v", err)
		return
	}

	if err = ctrl.rc.UpdateOne(withCancel, respmodel.QueryResponseUpdate{
		QueryId: id,
		Status:  s,
	}); err != nil {
		logger.Errorf("failed to update response: %v", err)
	}

	ctrl.mu.Lock()
	ctrl.processing[id] = cancel
	delete(ctrl.processing, id)
	logger.Debugf("processed %v", ctrl.processing)
	ctrl.mu.Unlock()
}

func (ctrl *Controller) CancelById(ctx context.Context, id int64) error {
	ctrl.mu.Lock()
	defer ctrl.mu.Unlock()

	cancel, ok := ctrl.processing[id]
	if !ok {
		return shared.ErrQueryIsNotProcessed
	}
	cancel()
	delete(ctrl.processing, id)
	logger.Infof("canceled query %d: %v", id, &ctrl.processing)

	if err := ctrl.rc.UpdateOne(ctx, respmodel.QueryResponseUpdate{
		QueryId: id,
		Status:  shared.CanceledStatus,
	}); err != nil {
		logger.Errorf("updating resp status to 'canceld' failed")
		return shared.ErrUpdateRecord
	}
	return nil
}

func (ctrl *Controller) CancelProcessing() {
	ctrl.mu.Lock()
	defer ctrl.mu.Unlock()

	for _, cancel := range ctrl.processing {
		cancel()
	}
}
