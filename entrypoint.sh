#!/bin/bash

echo "⏳ Waiting for Ollama service..."
# Ollama가 응답할 때까지 대기
until curl -s http://ollama:11434/api/tags > /dev/null; do
    sleep 2
done

echo "📥 Checking AI Model (gemma2:2b)..."
# 모델 다운로드 요청
curl -X POST http://ollama:11434/api/pull -d '{"name": "gemma2:2b"}'

echo "🚀 Starting MemoRa..."
exec "$@"