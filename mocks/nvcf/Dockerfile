# Use the official Go image as the base image
FROM golang:1.23.1

# Set the working directory inside the container
WORKDIR /app

# Copy the rest of the application code
COPY . .

# Build the Go binary
RUN go build -o main .

# Expose the port your application listens on (if applicable)
EXPOSE 8877

# Run the binary when the container starts
CMD ["./main"]
