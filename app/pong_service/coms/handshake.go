package coms

import "errors"

func handshake(jwt_token string) (int, error) {
	if jwt_token == "" {
		return 0, errors.New("jwt_token is required")
	}

	return 1, nil
}
