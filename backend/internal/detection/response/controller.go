package response

import (
	"context"

	"gagarin/internal/detection/response/model"
	"gagarin/internal/pb"
	"gagarin/internal/shared"
	"gagarin/pkg/storage/minios3"

	"github.com/yogenyslav/logger"
	"google.golang.org/grpc"
)

type responseRepo interface {
	InsertOne(ctx context.Context, params model.Response) error
	UpdateOne(ctx context.Context, params model.Response) error
	FindOneByQueryId(ctx context.Context, id int64) (model.ResultResponse, error)
}

type Controller struct {
	repo     responseRepo
	ml       pb.MlServiceClient
	s3client *minios3.S3
}

func NewController(repo responseRepo, mlConn *grpc.ClientConn, s3client *minios3.S3) *Controller {
	return &Controller{
		repo:     repo,
		ml:       pb.NewMlServiceClient(mlConn),
		s3client: s3client,
	}
}

func (ctrl *Controller) InsertOne(ctx context.Context, params model.QueryResponseCreate) error {
	resp := model.Response{
		QueryId: params.QueryId,
	}
	if err := ctrl.repo.InsertOne(ctx, resp); err != nil {
		logger.Errorf("failed to insert response: %v", err)
		return shared.ErrInsertRecord
	}
	return nil
}

func (ctrl *Controller) UpdateOne(ctx context.Context, params model.QueryResponseUpdate) error {
	resp := model.Response{
		QueryId: params.QueryId,
		Status:  params.Status,
	}
	if err := ctrl.repo.UpdateOne(ctx, resp); err != nil {
		logger.Errorf("failed to update response: %v", err)
		return shared.ErrUpdateRecord
	}
	return nil
}

func (ctrl *Controller) FindOneByQueryId(ctx context.Context, queryId int64) (model.ResultResponseDto, error) {
	var res model.ResultResponseDto

	response, err := ctrl.repo.FindOneByQueryId(ctx, queryId)
	if err != nil {
		logger.Errorf("failed to find response: %v", err)
		return res, shared.ErrFindRecord
	}

	in := &pb.ResultReq{Id: queryId}
	resp, err := ctrl.ml.FindResult(ctx, in)
	if err != nil {
		logger.Errorf("failed to find processed frames: %v", err)
		return res, shared.ErrFindResult
	}

	t, err := shared.StringFromQueryType(response.Type)
	if err != nil {
		return res, err
	}
	res.Type = t

	status, err := shared.StringFromResponseStatus(response.Status)
	if err != nil {
		return res, err
	}
	res.Status = status

	anomalies := resp.GetAnomalies()
	res.Anomalies = make([]model.Anomaly, len(anomalies))
	for idx, anomaly := range anomalies {
		res.Anomalies[idx].Ts = anomaly.GetTs()
		res.Anomalies[idx].Links = anomaly.GetLinks()
		res.Anomalies[idx].Cls = anomaly.GetCls()
	}

	return res, nil
}
