#!/bin/bash
docker build -t sap-ai-proxy .
docker stop sap-ai-proxy-container
docker rm sap-ai-proxy-container
docker run -d --name sap-ai-proxy-container -p 3001:3001 -v "$(pwd)/config.json:/app/config.json:ro" -v "$(pwd)/sap-ai-key.json:/app/sap-ai-key.json:ro" -v "/c/Users/10692/.aicore:/root/.aicore:ro" sap-ai-proxy
