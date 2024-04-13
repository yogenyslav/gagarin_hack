package shared

import (
	"strings"
)

type QueryType int

const (
	StreamType QueryType = iota
	VideoType
)

func StringFromQueryType(v QueryType) (string, error) {
	switch v {
	case StreamType:
		return "STREAM", nil
	case VideoType:
		return "VIDEO", nil
	default:
		return "", ErrWrongQueryType
	}
}

func QueryTypeFromString(v string) (QueryType, error) {
	switch strings.ToLower(v) {
	case "stream":
		return StreamType, nil
	case "video":
		return VideoType, nil
	default:
		return -1, ErrWrongQueryType
	}
}

type ResponseStatus int

const (
	ProcessingStatus ResponseStatus = iota
	SuccessStatus
	ErrorStatus
	CanceledStatus
)

func StringFromResponseStatus(v ResponseStatus) (string, error) {
	switch v {
	case ProcessingStatus:
		return "PROCESSING", nil
	case SuccessStatus:
		return "SUCCESS", nil
	case ErrorStatus:
		return "ERROR", nil
	case CanceledStatus:
		return "CANCELED", nil
	default:
		return "", ErrWrongResponseStatus
	}
}

func ResponseStatusFromString(v string) (ResponseStatus, error) {
	switch strings.ToLower(v) {
	case "processing":
		return ProcessingStatus, nil
	case "success":
		return SuccessStatus, nil
	case "error":
		return ErrorStatus, nil
	case "canceled":
		return CanceledStatus, nil
	default:
		return -1, ErrWrongResponseStatus
	}
}

type AnomalyClass int

const (
	BlurClass AnomalyClass = iota
	LightClass
	MotionClass
	OverlapClass
)

func StringFromAnomalyClass(v AnomalyClass) (string, error) {
	switch v {
	case BlurClass:
		return "BLUR", nil
	case LightClass:
		return "LIGHT", nil
	case MotionClass:
		return "MOTION", nil
	case OverlapClass:
		return "OVERLAP", nil
	default:
		return "", ErrWrongAnomalyClass
	}
}

func AnomalyClassFromString(v string) (AnomalyClass, error) {
	switch strings.ToLower(v) {
	case "blur":
		return BlurClass, nil
	case "light":
		return LightClass, nil
	case "motion":
		return MotionClass, nil
	case "overlap":
		return OverlapClass, nil
	default:
		return -1, ErrWrongAnomalyClass
	}
}

const (
	UniqueViolationCode = "23505"
	VideoBucket         = "video"
)
