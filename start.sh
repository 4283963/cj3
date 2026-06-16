#!/bin/bash

echo "🚀 启动流浪猫狗救助领养系统"

echo "📦 安装后端依赖..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "🗄️  请确保 MySQL 数据库已启动，并创建好数据库"
echo "   数据库配置在 backend/.env 文件中修改"

echo "🔧 启动后端服务 (端口 8000)..."
python main.py &
BACKEND_PID=$!

echo "🌐 安装前端依赖..."
cd ../frontend
npm install

echo "🎨 启动前端服务 (端口 5173)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 系统启动完成！"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo "   前端地址: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait
