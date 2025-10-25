"""
FastAPI主应用 - 账单查询与管理系统API
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import os

# 导入自定义模块
from .database import db_manager, init_database
from .bill_query import query_processor
from .cost_analysis import cost_analyzer
from .ai_services import user_profiler, recommendation_engine, intelligent_analyzer
from .invoice_ocr import invoice_ocr_processor
from .data_cleaning import data_cleaner
from .config import HOST, PORT, API_V1_PREFIX

# 创建FastAPI应用
app = FastAPI(
    title="账单查询与管理系统",
    description="智能账单查询、消费分析、发票管理的综合系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型定义
class BillCreate(BaseModel):
    consume_time: datetime
    amount: float
    merchant: str
    category: Optional[str] = "未知"
    payment_method: str
    location: Optional[str] = None
    description: Optional[str] = None

class BillUpdate(BaseModel):
    consume_time: Optional[datetime] = None
    amount: Optional[float] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    user_id: int = 1

class AnalysisRequest(BaseModel):
    user_id: int = 1
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class InvoiceProcessRequest(BaseModel):
    ocr_text: str
    user_id: int = 1
    file_path: Optional[str] = None

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_database()
    print("数据库初始化完成")

# 根路径
@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径返回欢迎页面"""
    return """
    <html>
        <head>
            <title>账单查询与管理系统</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>账单查询与管理系统</h1>
            <p>欢迎使用智能账单查询与管理系统！</p>
            <ul>
                <li><a href="/docs">API文档</a></li>
                <li><a href="/redoc">ReDoc文档</a></li>
                <li><a href="/api/v1/bills">账单列表</a></li>
                <li><a href="/api/v1/analysis/summary">消费分析</a></li>
            </ul>
        </body>
    </html>
    """

# 账单管理API
@app.post(f"{API_V1_PREFIX}/bills")
async def create_bill(bill: BillCreate, user_id: int = 1):
    """创建账单记录"""
    try:
        # 数据清洗
        bill_data = data_cleaner.clean_bill_data(bill.dict())
        bill_data['user_id'] = user_id
        
        # 创建账单
        created_bill = db_manager.create_bill(bill_data)
        
        return {
            "success": True,
            "message": "账单创建成功",
            "bill_id": created_bill.id,
            "data": {
                "id": created_bill.id,
                "consume_time": created_bill.consume_time.isoformat(),
                "amount": created_bill.amount,
                "merchant": created_bill.merchant,
                "category": created_bill.category,
                "payment_method": created_bill.payment_method
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建账单失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/bills")
async def get_bills(user_id: int = 1, limit: int = 100, offset: int = 0):
    """获取账单列表"""
    try:
        bills = db_manager.get_bills(user_id, limit, offset)
        
        return {
            "success": True,
            "data": [
                {
                    "id": bill.id,
                    "consume_time": bill.consume_time.isoformat(),
                    "amount": bill.amount,
                    "merchant": bill.merchant,
                    "category": bill.category,
                    "payment_method": bill.payment_method,
                    "location": bill.location,
                    "description": bill.description,
                    "created_at": bill.created_at.isoformat()
                }
                for bill in bills
            ],
            "total": len(bills)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账单列表失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/bills/{{bill_id}}")
async def get_bill(bill_id: int, user_id: int = 1):
    """获取单个账单详情"""
    try:
        bills = db_manager.get_bills(user_id, limit=1000)
        bill = next((b for b in bills if b.id == bill_id), None)
        
        if not bill:
            raise HTTPException(status_code=404, detail="账单不存在")
        
        return {
            "success": True,
            "data": {
                "id": bill.id,
                "consume_time": bill.consume_time.isoformat(),
                "amount": bill.amount,
                "merchant": bill.merchant,
                "category": bill.category,
                "payment_method": bill.payment_method,
                "location": bill.location,
                "description": bill.description,
                "created_at": bill.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账单详情失败: {str(e)}")

@app.put(f"{API_V1_PREFIX}/bills/{{bill_id}}")
async def update_bill(bill_id: int, bill_update: BillUpdate, user_id: int = 1):
    """更新账单记录"""
    try:
        # 过滤掉None值
        update_data = {k: v for k, v in bill_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供更新数据")
        
        # 数据清洗
        if update_data:
            update_data = data_cleaner.clean_bill_data(update_data)
        
        # 更新账单
        updated_bill = db_manager.update_bill(bill_id, update_data)
        
        if not updated_bill:
            raise HTTPException(status_code=404, detail="账单不存在")
        
        return {
            "success": True,
            "message": "账单更新成功",
            "data": {
                "id": updated_bill.id,
                "consume_time": updated_bill.consume_time.isoformat(),
                "amount": updated_bill.amount,
                "merchant": updated_bill.merchant,
                "category": updated_bill.category,
                "payment_method": updated_bill.payment_method
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新账单失败: {str(e)}")

@app.delete(f"{API_V1_PREFIX}/bills/{{bill_id}}")
async def delete_bill(bill_id: int, user_id: int = 1):
    """删除账单记录"""
    try:
        success = db_manager.delete_bill(bill_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="账单不存在")
        
        return {
            "success": True,
            "message": "账单删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除账单失败: {str(e)}")

# 智能查询API
@app.post(f"{API_V1_PREFIX}/query")
async def intelligent_query(request: QueryRequest):
    """智能查询接口"""
    try:
        # 解析查询
        parsed_query = query_processor.parse_query(request.query)
        
        # 执行查询
        result = query_processor.execute_query(parsed_query, request.user_id)
        
        return {
            "success": True,
            "query": request.query,
            "parsed_query": parsed_query,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

# 消费分析API
@app.get(f"{API_V1_PREFIX}/analysis/summary")
async def get_spending_summary(user_id: int = 1, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """获取消费汇总统计"""
    try:
        summary = db_manager.get_spending_summary(user_id, start_date, end_date)
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消费汇总失败: {str(e)}")

@app.post(f"{API_V1_PREFIX}/analysis/comprehensive")
async def get_comprehensive_analysis(request: AnalysisRequest):
    """获取综合分析报告"""
    try:
        analysis = cost_analyzer.get_spending_analysis(
            request.user_id, 
            request.start_date, 
            request.end_date
        )
        
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析报告失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/analysis/category")
async def get_category_analysis(user_id: int = 1, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """获取分类消费分析"""
    try:
        analysis = cost_analyzer.get_category_analysis(user_id, start_date, end_date)
        
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类分析失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/analysis/trend")
async def get_trend_analysis(user_id: int = 1, period: str = "monthly"):
    """获取趋势分析"""
    try:
        analysis = cost_analyzer.get_trend_analysis(user_id, period)
        
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取趋势分析失败: {str(e)}")

# AI服务API
@app.get(f"{API_V1_PREFIX}/ai/profile/{{user_id}}")
async def get_user_profile(user_id: int):
    """获取用户画像"""
    try:
        profile = user_profiler.generate_user_profile(user_id)
        
        return {
            "success": True,
            "data": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户画像失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/ai/recommendations/financial/{{user_id}}")
async def get_financial_recommendations(user_id: int):
    """获取金融产品推荐"""
    try:
        recommendations = recommendation_engine.get_financial_recommendations(user_id)
        
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取金融推荐失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/ai/recommendations/spending/{{user_id}}")
async def get_spending_recommendations(user_id: int):
    """获取消费建议"""
    try:
        recommendations = recommendation_engine.get_spending_recommendations(user_id)
        
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消费建议失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/ai/analysis/comprehensive/{{user_id}}")
async def get_comprehensive_ai_analysis(user_id: int):
    """获取综合AI分析"""
    try:
        analysis = intelligent_analyzer.generate_comprehensive_analysis(user_id)
        
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI分析失败: {str(e)}")

# 发票管理API
@app.post(f"{API_V1_PREFIX}/invoices/process")
async def process_invoice(request: InvoiceProcessRequest):
    """处理发票OCR文本"""
    try:
        result = invoice_ocr_processor.create_invoice_record(
            request.ocr_text,
            request.file_path,
            request.user_id
        )
        
        return {
            "success": result.get("success", False),
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理发票失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/invoices")
async def get_invoices(user_id: int = 1, limit: int = 100):
    """获取发票列表"""
    try:
        invoices = db_manager.get_invoices(user_id, limit)
        
        return {
            "success": True,
            "data": [
                {
                    "id": invoice.id,
                    "invoice_time": invoice.invoice_time.isoformat(),
                    "amount": invoice.amount,
                    "merchant": invoice.merchant,
                    "invoice_type": invoice.invoice_type,
                    "file_path": invoice.file_path,
                    "created_at": invoice.created_at.isoformat()
                }
                for invoice in invoices
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取发票列表失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/invoices/statistics")
async def get_invoice_statistics(user_id: int = 1):
    """获取发票统计信息"""
    try:
        stats = invoice_ocr_processor.get_invoice_statistics(user_id)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取发票统计失败: {str(e)}")

# 数据清洗API
@app.post(f"{API_V1_PREFIX}/data/clean")
async def clean_bill_data(bill_data: Dict[str, Any]):
    """清洗账单数据"""
    try:
        cleaned_data = data_cleaner.clean_bill_data(bill_data)
        
        return {
            "success": True,
            "original_data": bill_data,
            "cleaned_data": cleaned_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据清洗失败: {str(e)}")

@app.post(f"{API_V1_PREFIX}/data/validate")
async def validate_bill_data(bills: List[Dict[str, Any]]):
    """验证账单数据质量"""
    try:
        quality_report = data_cleaner.validate_data_quality(bills)
        anomalies = data_cleaner.detect_anomalies(bills)
        
        return {
            "success": True,
            "quality_report": quality_report,
            "anomalies": anomalies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据验证失败: {str(e)}")

# 健康检查
@app.get(f"{API_V1_PREFIX}/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
