---
title: "Comparing Round Robin and Least Connections in Nginx Load Balancing"
date: 2024-12-10 21:00:00 +0900
categories: [NestJS]
tags: [NestJS, Docker, Nginx, Round Robin, Least Connections, ELK]
---



# Introduction

In this blog, we explore the differences between **Round Robin** and **Least Connections** load balancing algorithms using a test setup with Nginx, Nest.js, and monitoring via ELK Stack (Elasticsearch, Logstash, Kibana).

---

## What are Round Robin and Least Connections?

- **Round Robin**: Assigns requests sequentially to servers. and Round Robin is a type of static load balancing approach
![Round Robin](https://media.geeksforgeeks.org/wp-content/uploads/20240420165556/Screenshot-2024-04-20-165542.png)

- **Least Connections**: Assigns requests to the server with the fewest active connections. and Least Connections is a type of dynamic load balancing approach
![Least Connections](https://media.geeksforgeeks.org/wp-content/uploads/20240420170819/Screenshot-2024-04-20-170800.png)

---

## Step: 1. Test Setup

### Architecture
- **Nginx**: Acts as the load balancer.
- **Backend Servers**: Four Nest.js servers.
- **ELK Stack**: Logs from Nginx are visualized in Kibana.

### Configuration
#### Nginx Configuration (`nginx.conf`)
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$upstream_addr $upstream_response_time';

    access_log /var/log/nginx/access.log main;

    upstream backend {
        least_conn;
        server app1:3000;
        server app2:3000;
        server app3:3000;
        server app4:3000;
    }

    server {
        listen 80;

        location /fixed-delay {
            proxy_pass http://backend; # Round Robin or Least Connections
        }

        location /random-delay {
            proxy_pass http://backend; # Round Robin or Least Connections
        }

        location /cpu-intensive {
            proxy_pass http://backend; # Round Robin or Least Connections
        }
    }
}
```

#### Nest.js App (`app.controller.ts`)
```typescript
import { Controller, Get, Query } from '@nestjs/common';

@Controller()
export class AppController {
  // API with fixed delays (Basic API for step-by-step testing)
  @Get('/fixed-delay')
  async fixedDelay(@Query('requestId') requestId: string): Promise<string> {
    // Calculate delay based on the request ID (repeats between 1 second and 4 seconds)
    const id = parseInt(requestId || '0', 10);
    const delayOptions = [1000, 2000, 3000, 4000];
    const delay = delayOptions[(id - 1) % delayOptions.length]; // 1부터 시작하는 순서

    // Hold the connection for the calculated delay duration
    await new Promise((resolve) => setTimeout(resolve, delay));

    return `RequestId: ${requestId} => Processed by ${process.env.APP_NAME || 'API Server'} in ${delay} ms\n`;
  }

  // API with random delays (For irregular load testing)
  @Get('/random-delay')
  async randomDelay(@Query('requestId') requestId: string): Promise<string> {
    // Random delay between 500ms and 5000ms
    const delay = Math.floor(Math.random() * 4500) + 500;

    // Hold the connection for the calculated delay duration
    await new Promise((resolve) => setTimeout(resolve, delay));

    return `RequestId: ${requestId} => Processed by ${process.env.APP_NAME || 'API Server'} in ${delay} ms\n`;
  }

  // API simulating CPU-intensive tasks
  @Get('/cpu-intensive')
  async cpuIntensive(@Query('requestId') requestId: string): Promise<string> {
    const id = parseInt(requestId || '0', 10);
    const delay = ((id % 3) + 1) * 1000; // Task duration between 1 and 3 seconds

    // Simulate CPU-intensive work
    const start = Date.now();
    while (Date.now() - start < delay) {
      // CPU computation
    }

    return `RequestId: ${requestId} => Processed by ${process.env.APP_NAME || 'API Server'} after CPU-intensive task of ${delay} ms\n`;
  }
}
```

#### Logstash Configuration (`logstash.conf`)
```plaintext
input {
  file {
    path => "/var/log/nginx/access.log" 
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }
}

filter {
    grok {
        match => {
            "message" => '%{IPORHOST:remote_addr} - %{DATA:remote_user} \[%{HTTPDATE:timestamp}\] "%{WORD:method} %{DATA:request} HTTP/%{NUMBER:http_version}" %{NUMBER:status} %{NUMBER:bytes} "%{DATA:referrer}" "%{DATA:agent}" %{DATA:upstream_addr} %{NUMBER:upstream_response_time}'
        }
    }
    date {
        match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
        target => "@timestamp"
    }
}


output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "nginx-logs"
  }
  stdout { codec => rubydebug }
}
```

---

## Step: 2. Testing

### Test Script
The test uses a Bash script to send sequential requests to the Nginx server:
```bash
#!/bin/bash

url="http://localhost:8080/cpu-intensive" # Nginx Container URL
concurrent_requests=(600 700 800 900) 
total_requests=(1200 1400 1600 1800) 
algorithm=LeastConnections # algorithm name (RoundRobin or LeastConnections)

if [[ -z $algorithm ]]; then
  echo "Usage: $0 <Algorithm>"
  echo "Algorithm should be either 'RoundRobin' or 'LeastConnections'"
  exit 1
fi

echo "Starting load test for $algorithm algorithm..."

# check start time
overall_start_time=$(date +%s)

# Step-by-Step Test
for i in "${!concurrent_requests[@]}"; do
  concurrent="${concurrent_requests[$i]}"
  total="${total_requests[$i]}"

  echo "Testing with $total total requests and $concurrent concurrent requests..."
  
  # Perform the test using Apache Benchmark
  ab -n "$total" -c "$concurrent" "$url" > "results_${algorithm}_${total}_${concurrent}.txt"

  echo "Completed test for $total requests and $concurrent concurrent requests."
done

# check end time
overall_end_time=$(date +%s)
overall_elapsed_time=$((overall_end_time - overall_start_time))

echo "Load test completed for $algorithm algorithm!"
echo "Total time taken: ${overall_elapsed_time} seconds"
```

### Observations
- **Round Robin**:
  - Requests are distributed sequentially across servers.
  - Servers with higher delay times (e.g., 4s) may process fewer requests.
  - Total time is influenced by the longest delay in the batch.

- **Least Connections**:
  - Requests tend to cluster on servers with shorter processing times.
  - High-delay servers (e.g., 4s) receive fewer requests.
  - Total time is reduced as shorter delays dominate the allocation.

---

## 3. Visualization in Kibana

### Metrics to Monitor
- **Requests Per Second (RPS)**: Number of requests handled over time.
- **Response Times**: Average response time per server.
- **Server Load Distribution**: Total requests handled by each server.

### Steps in Kibana
1. Navigate to **Dashboard**.
2. Create visualizations for:
   - **Requests Per Server**: Use `terms` aggregation on `upstream_addr`.
   - **Average Response Time**: Use `average` aggregation on response time.
   - **Request Timeline**: Use `date histogram` on `@timestamp`.

---


# Conclusion

Today, I explored the differences between the load balancing algorithms, **Round Robin** and **Least Connections**, in Nginx. I also tested them and used the ELK stack for logging and visualization.

Theoretically, the Round Robin algorithm should distribute requests sequentially (1, 2, 3, 4) across four servers. 
However, I noticed that Nginx processes requests in parallel, leading to non-sequential distribution. 
This could be due to issues in my code or testing method, so I'll need to investigate further.

Despite not achieving fully satisfying results in this simple test setup, 
the experiment helped me understand the differences between the two algorithms. 
With a clearer understanding, I believe that during real-world scenarios with high workloads, 
using ELK for analysis and comparison can guide us toward choosing the optimal algorithm for better performance.

<!-- 오늘은 nginx 로드밸런싱의 알고리즘인 round robin과 Least Connections의 차이점을 알아보고 테스트해서 ELK stack으로 로그 및 시각화 하는것을 해봤습니다.
근데 이론상 round robin은 서버가 4개였기 때문에 1,2,3,4 순서대로 분배를 해야 됐지만 nginx 자체에서 병렬로 처리를 해서 순서대로 분배 되지 않는것을 확인했습니다.
이 부분은 제가 코드를 잘 못 짰거나 테스트 방법이 잘 못 됐을 수도 있습니다. (좀 더 연구를 해봐야 겠군요..!)
그래도 두 알고리즘의 차이를 알 수 있는 연구였던것 같습니다.
간단한 프로세스로 테스트를 해서 만족하는 결과를 얻지 못했지만 
실제 서비스를 운영할때 부하가 걸리는 작업이 있을때 ELK로 비교 분석하여 
더 좋은 알고리즘을 적용할 수있는 전략을 가져볼수 있을것같습니다.  -->


Thank you for reading, and happy blogging! 🚀

## References

- [Reference](https://www.researchgate.net/publication/366834494_Load_Balancing_Analysis_Using_Round-Robin_and_Least-Connection_Algorithms_for_Server_Service_Response_Time#:~:text=research%20%5B17%5D.,Figure%201.)
- [Reference](https://www.geeksforgeeks.org/network-load-balancing-round-robin-vs-least-connections/)
- [Sample Github](https://github.com/hoonapps/nginx-balancer-algorithms-elk-test)


