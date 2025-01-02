```markdown


# Get Started Guide

Follow these steps to set up and run the project.

## Prerequisites

- Docker
- Docker Compose
- Python 3.11
- pip

## Setup

### 1. Clone the Repository

Clone the repository to your local machine:

```sh
git clone https://github.com/RowMax03/transcendence.git
cd transcendence
```

### 2. Create a `.env` File

Create a `.env` file in the `/app` directory (next to `docker-compose.yml`) with the following content:

```env
CLIENT_ID=your-client-id  # Replace with your OAuth client ID
CLIENT_SECRET=your-client-secret  # Replace with your OAuth client secret
REDIRECT_URI_IDENTITY_PROVIDER=https://login.provider/auth  # Replace with your identity provider's redirect URI
REDIRECT_URI=http://localhost:80/home  # Replace with your application's redirect URI
JWT_SECRET=your-jwt-secret  # Replace with a secure secret key for JWT
BASE_REDIRECT_URI=http://localhost:8001/home  # Replace with your application's base redirect URI
```

Replace the placeholder values with your actual credentials and settings:

- `CLIENT_ID`: The client ID provided by your OAuth provider.
- `CLIENT_SECRET`: The client secret provided by your OAuth provider.
- `REDIRECT_URI_IDENTITY_PROVIDER`: The URI to which the identity provider will redirect after authentication.
- `REDIRECT_URI`: The URI to which your application will redirect after authentication.
- `JWT_SECRET`: A secure secret key used for signing JSON Web Tokens (JWT). Make sure this is a strong, random string.
- `BASE_REDIRECT_URI`: The base URI for redirects within your application.

Example:

```env
CLIENT_ID=u-s4t2ud-fa3ef9e8cac10a1250eb6fc207a67297aasddasa3e6e652d4f812a12314d
CLIENT_SECRET=s-s4t2ud-fa3ef9e8cac10a1250eb6fc207a672asdasb3eef3e6e652d4f812a12314d
REDIRECT_URI_IDENTITY_PROVIDER=https://api.intra.42.fr/oauth/authorize
REDIRECT_URI=http://localhost:80/home
JWT_SECRET=supersecuresecretkey12345
BASE_REDIRECT_URI=http://localhost:8001/home
```

Make sure to keep your `.env` file secure and do not commit it to version control.
```

This refined section provides clearer instructions and example values for setting up the `.env` file.
This refined section provides clearer instructions and example values for setting up the `.env` file.

### 3. Build and Run the Docker Containers

Build and run the Docker containers using Docker Compose:

```sh
docker-compose up --build
```

This command will build the Docker images and start the containers.

### 4. Access the Application

Once the containers are up and running, you can access the application in your web browser at:

```
http://localhost:8001
```

## Development

### Running the Development Server

To run the Django development server with auto-reload, use the following command:

```sh
docker-compose exec web python manage.py runserver 0.0.0.0:8000
```

### Running Migrations

To apply database migrations, use the following command:

```sh
docker-compose exec web python manage.py migrate
```

### Creating a Superuser

To create a superuser for accessing the Django admin, use the following command:

```sh
docker-compose exec web python manage.py createsuperuser
```

### Collecting Static Files

To collect static files, use the following command:

```sh
docker-compose exec web python manage.py collectstatic
```

## Troubleshooting

### Common Issues

- **Database Connection Issues**: Ensure that the database container is running and accessible.
- **Environment Variables**: Double-check that all required environment variables are set correctly in the `.env` file.
- **Docker Compose**: Ensure you are using the correct version of Docker Compose.

### Logs

To view the logs of a specific container, use the following command:

```sh
docker-compose logs <container_name>
```

Replace `<container_name>` with the name of the container you want to view logs for.

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

By following this guide, you should be able to set up and run the project successfully. If you encounter any issues, refer to the troubleshooting section or consult the additional resources provided.
```

This guide provides a comprehensive overview of the steps needed to set up and run your project, including prerequisites, setup instructions, and common troubleshooting tips.
This guide provides a comprehensive overview of the steps needed to set up and run your project, including prerequisites, setup instructions, and common troubleshooting tips.
