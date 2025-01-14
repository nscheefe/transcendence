FROM golang:1.23.3

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download
RUN go install github.com/mitranim/gow@latest
COPY . .

ENTRYPOINT ["gow", "run", "main.go"]
