package pkg

import (
	"time"
)

func GetLocalTime() time.Time {
	return time.Now().UTC().Add(3 * time.Hour)
}
