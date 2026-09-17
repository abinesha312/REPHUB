#!/bin/bash
# Simple API test script

API_URL="http://localhost:8000"

echo "Testing Resume Repository API..."
echo ""

# Test health endpoint
echo "1. Health Check:"
curl -s "${API_URL}/api/health" | python -m json.tool
echo ""
echo ""

# Test list resumes (should be empty initially)
echo "2. List Resumes:"
curl -s "${API_URL}/api/resumes/list" | python -m json.tool
echo ""
echo ""

# Test folders endpoint
echo "3. List Folders:"
curl -s "${API_URL}/api/resumes/folders" | python -m json.tool
echo ""

echo "API is responding!"
