FROM golang:1.23.3 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download
COPY . .

RUN go build -o main *.go

# Use a minimal base image to run the application
FROM gcr.io/distroless/base-debian12

WORKDIR /app

COPY --from=builder /app/main .

CMD ["./main"]