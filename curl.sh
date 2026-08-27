#!/bin/bash
BASE_URL="http://127.0.0.1:8000"

echo " HEALTHY LIVE "
curl "$BASE_URL/health/live"
echo

echo " HEALTH READY "
curl "$BASE_URL/health/ready"
echo

echo " CREATE "
curl -X POST "$BASE_URL/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cuoi tuan",
    "description": "Mot ngay cuoi tuan on ao va met moi",
    "completed": false,
    "priority": 1
   }'
echo

echo " GET LIST "
curl "$BASE_URL/todos"
echo

echo " GET DETAIL "
curl "$BASE_URL/todos/1"
echo

echo " UPDATE "
curl -X PUT "$BASE_URL/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true,
    "priority": 3
   }'
echo

echo " DELETE "
curl -X DELETE "$BASE_URL/todos/1"
echo
