# FastAPI Deployment on Ubuntu as a Service

This guide provides step-by-step instructions to deploy a FastAPI application on an Ubuntu server using systemd and Nginx.

## Prerequisites

- Ubuntu 20.04 or later
- Python 3.8 or later
- FastAPI application
- Virtual environment for Python
- Uvicorn ASGI server
- Nginx

## Setup FastAPI Application

1. **Clone your FastAPI application repository:**
    ```sh
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required packages:**
    ```sh
    pip install fastapi uvicorn
    ```

## Create a systemd Service

1. **Create a new service file for the FastAPI application:**
    ```sh
    sudo nano /etc/systemd/system/fastapi.service
    ```

2. **Add the following content to the `fastapi.service` file:**
    ```ini
    [Unit]
    Description=FastAPI Service
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/path/to/your/repo
    Environment="PATH=/path/to/your/repo/venv/bin"
    ExecStart=/path/to/your/repo/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

    [Install]
    WantedBy=multi-user.target
    ```

    Replace `/path/to/your/repo` with the actual path to your FastAPI application.

3. **Start and enable the service:**
    ```sh
    sudo systemctl daemon-reload
    sudo systemctl start fastapi
    sudo systemctl enable fastapi
    ```

4. **Check the status of the service:**
    ```sh
    sudo systemctl status fastapi
    ```

## Configure Nginx as a Reverse Proxy

1. **Install Nginx:**
    ```sh
    sudo apt update
    sudo apt install nginx
    ```

2. **Create a new Nginx configuration file for the FastAPI service:**
    ```sh
    sudo nano /etc/nginx/sites-available/fastapi
    ```

3. **Add the following content to the `fastapi` file:**
    ```nginx
    server {
        listen 80;
        server_name your_domain_or_IP;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

    Replace `your_domain_or_IP` with your domain name or server's IP address.

4. **Enable the new configuration by creating a symbolic link:**
    ```sh
    sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled
    ```

5. **Test the Nginx configuration:**
    ```sh
    sudo nginx -t
    ```

6. **Restart Nginx:**
    ```sh
    sudo systemctl restart nginx
    ```

## Firewall Configuration

1. **Allow Nginx Full on the firewall:**
    ```sh
    sudo ufw allow 'Nginx Full'
    ```

## Conclusion

Your FastAPI application should now be running as a service on Ubuntu, with Nginx acting as a reverse proxy to forward requests to Uvicorn. You can visit your domain or IP address in a web browser to see your FastAPI application in action.

## Additional Notes

- Ensure your domain's DNS settings are correctly pointing to your server's IP address.
- For production use, consider setting up SSL using Let's Encrypt.

---

By following this guide, you should have a robust deployment setup for your FastAPI application on an Ubuntu server. If you encounter any issues, check the logs for both the FastAPI service and Nginx to diagnose problems.
