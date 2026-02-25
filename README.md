# DNS-Based Fibonacci Service

## Component Port Mapping
| Component | Port | Protocol | Docker Mapping |
|-----------|------|----------|----------------|
| Authoritative Server (AS) | 53533 | UDP | 53533:53533/udp |
| Fibonacci Server (FS) | 9090 | TCP | 9090:9090/tcp |
| User Server (US) | 8080 | TCP | 8080:8080/tcp |

## Project Structure
```
dns_app/
├── AS/
│   ├── authoritative_server.py
│   └── Dockerfile
├── FS/
│   ├── fibonacci_server.py
│   └── Dockerfile
└── US/
    ├── user_server.py
    └── Dockerfile
```

## Docker Deployment
### Prerequisites
- Docker Desktop
- curl

### Deployment Steps
```bash
docker network create dns_network

cd C:\Users\19367\Desktop\dns_app\AS
docker build --no-cache -t dns-as:latest .
docker run --network dns_network --name as -p 53533:53533/udp -d dns-as:latest
docker ps --filter "name=as"

cd C:\Users\19367\Desktop\dns_app\FS
docker build --no-cache -t dns-fs:latest .
docker run --network dns_network --name fs -p 9090:9090 -d dns-fs:latest
docker ps --filter "name=fs"

cd C:\Users\19367\Desktop\dns_app\US
docker build --no-cache -t dns-us:latest .
docker run --network dns_network --name us -p 8080:8080 -d dns-us:latest
docker ps --filter "name=us"
```

### Validation Commands
```bash
docker ps --filter "name=as" --filter "name=fs" --filter "name=us"
docker logs as
docker logs fs
docker logs us
docker stop as fs us
docker rm as fs us
docker network rm dns_network
```

### End-to-End Testing
```bash
for /f "tokens=*" %i in ('docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" as') do set AS_IP=%i
for /f "tokens=*" %i in ('docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" fs') do set FS_IP=%i

curl -X PUT -H "Content-Type: application/json" -d "{\"hostname\":\"fibonacci.com\",\"ip\":\"%FS_IP%\",\"as_ip\":\"%AS_IP%\",\"as_port\":\"53533\"}" http://localhost:9090/register
curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=%AS_IP%&as_port=53533"
```

### Troubleshooting
```bash
# Container name conflict
docker stop as && docker rm as
docker stop fs && docker rm fs
docker stop us && docker rm us

# FS port mismatch (9091)
docker run --network dns_network --name fs -p 9090:9090 -p 9091:9091 -d dns-fs:latest
curl -X PUT -H "Content-Type: application/json" -d "{\"hostname\":\"fibonacci.com\",\"ip\":\"%FS_IP%\",\"as_ip\":\"%AS_IP%\",\"as_port\":\"53533\"}" http://localhost:9091/register
```
