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
from .database import db_manager
from fix_sqlalchemy_session import get_bills_simple, get_bill_by_id, create_bill_simple, get_spending_summary_simple
from .database import init_database
from .bill_query import query_processor
from .cost_analysis import cost_analyzer
from .ai_services import user_profiler, recommendation_engine, intelligent_analyzer
from .invoice_ocr import invoice_ocr_processor
from .data_cleaning import data_cleaner
from .config import HOST, PORT, API_V1_PREFIX
import sqlite3

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
    # 确保 OCR 日用量表存在
    try:
        conn = sqlite3.connect(str((__import__('pathlib').Path(__file__).parent.parent / 'data' / 'bill_db.sqlite')))
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ocr_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            used_at DATE NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            UNIQUE(user_id, used_at)
        )
        """)
        conn.commit()
        conn.close()
    except Exception as _:
        pass

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
        bills = get_bills_simple(user_id, limit, offset)
        
        return {
            "success": True,
            "data": bills,
            "total": len(bills)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账单列表失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/bills/{{bill_id}}")
async def get_bill(bill_id: int, user_id: int = 1):
    """获取单个账单详情"""
    try:
        bill = get_bill_by_id(bill_id)
        
        if not bill or bill['user_id'] != user_id:
            raise HTTPException(status_code=404, detail="账单不存在")
        
        return {
            "success": True,
            "data": bill
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
        summary = get_spending_summary_simple(user_id)
        
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

# 前端与OCR整合：发票图片上传并OCR
@app.post(f"{API_V1_PREFIX}/invoices/upload")
async def upload_invoice_image(file: UploadFile = File(...), user_id: int = 1):
    """上传发票图片并进行OCR，返回入库结果"""
    try:
        # 非订阅用户每日10次限额（演示）
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            db_path = str((__import__('pathlib').Path(__file__).parent.parent / 'data' / 'bill_db.sqlite'))
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT count FROM ocr_usage WHERE user_id=? AND used_at=?", (user_id, today))
            row = cur.fetchone()
            current = row[0] if row else 0
            if current >= 10:
                conn.close()
                raise HTTPException(status_code=429, detail="OCR当日次数已达上限(10)。请订阅提升配额或次日再试。")
            if row:
                cur.execute("UPDATE ocr_usage SET count=count+1 WHERE user_id=? AND used_at=?", (user_id, today))
            else:
                cur.execute("INSERT INTO ocr_usage(user_id, used_at, count) VALUES(?,?,1)", (user_id, today))
            conn.commit()
            conn.close()
        except HTTPException:
            raise
        except Exception as _:
            pass
        # 保存上传文件
        from .config import UPLOADS_DIR
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        save_path = os.path.join(str(UPLOADS_DIR), file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())

        # 这里可接入真实OCR；当前以文件名作为占位OCR文本
        ocr_text = f"发票图片: {file.filename}"
        result = invoice_ocr_processor.create_invoice_record(
            ocr_text=ocr_text,
            file_path=save_path,
            user_id=user_id,
        )

        return {
            "success": result.get("success", False),
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传并处理发票失败: {str(e)}")

# 可选：挂载前端静态资源（若存在web目录）
try:
    web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
    if os.path.isdir(web_dir):
        app.mount("/app", StaticFiles(directory=web_dir, html=True), name="app")
except Exception:
    pass

# 商家评估Top榜（频率/复购/间隔）
@app.get(f"{API_V1_PREFIX}/merchants/top")
async def get_top_merchants(user_id: int = 1, window: int = 90, top_k: int = 10):
    """近window天用户商家评估Top榜"""
    try:
        # 取近window天账单
        from datetime import timedelta
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=window)
        bills = get_bills_simple(user_id=user_id, limit=10000, offset=0)
        bills = [b for b in bills if b.get('consume_time') and str(b['consume_time']) >= start_dt.strftime('%Y-%m-%d')]

        # 聚合
        by_merchant = {}
        for b in bills:
            m = b.get('merchant') or '未知'
            by_merchant.setdefault(m, []).append(b)

        results = []
        for m, arr in by_merchant.items():
            arr_sorted = sorted(arr, key=lambda x: str(x.get('consume_time')))
            visits = len(arr_sorted)
            total_amount = sum(float(x.get('amount') or 0) for x in arr_sorted)
            repurchase = 1.0 if visits >= 2 else 0.0  # 单用户退化定义
            # 平均间隔天数
            intervals = []
            for i in range(1, len(arr_sorted)):
                try:
                    t1 = datetime.fromisoformat(str(arr_sorted[i]['consume_time']).replace(' ', 'T'))
                    t0 = datetime.fromisoformat(str(arr_sorted[i-1]['consume_time']).replace(' ', 'T'))
                    intervals.append((t1 - t0).days or 0)
                except Exception:
                    pass
            avg_interval = sum(intervals)/len(intervals) if intervals else None
            # 简易评分：访问频次+复购+金额占比权重
            score = visits*0.5 + repurchase*1.5 + (total_amount/ (1+total_amount))
            results.append({
                'merchant': m,
                'visits': visits,
                'total_amount': round(total_amount,2),
                'repurchase_rate': repurchase,
                'avg_interval_days': avg_interval,
                'score': round(score,3)
            })

        results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
        return { 'success': True, 'data': results }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商家Top失败: {str(e)}")

# AI助手意图增强
@app.post(f"{API_V1_PREFIX}/ai/advice/{{user_id}}")
async def ai_advice(user_id: int, body: Dict[str, Any]):
    """对话式AI助手：今日/趋势/好商家/预警"""
    try:
        q = (body.get('query') or '').strip()
        today_str = datetime.now().strftime('%Y-%m-%d')
        # 今日
        if any(k in q for k in ['今日','今天','today']):
            bills = get_bills_simple(user_id=user_id, limit=1000)
            tb = [b for b in bills if str(b.get('consume_time','')).startswith(today_str)]
            total = sum(float(x.get('amount') or 0) for x in tb)
            topm = None
            if tb:
                from collections import Counter
                topm = Counter([x.get('merchant') for x in tb]).most_common(1)[0][0]
            return { 'cards': [
                { 'type':'summary', 'title':'今日消费', 'content': f"{len(tb)} 笔，共 {total:.2f} 元" },
                { 'type':'tip', 'title':'提示', 'content': f"今日最常去：{topm or '—'}" }
            ]}
        # 趋势
        if any(k in q for k in ['趋势','trend','近7','近30']):
            s = get_spending_summary_simple(user_id)
            return { 'cards': [
                { 'type':'summary', 'title':'趋势概览', 'content': f"总金额 {float(s.get('total_amount',0)):.2f} 元，单笔均值 {float(s.get('avg_amount',0)):.2f} 元"},
            ]}
        # 好商家
        if any(k in q for k in ['好商家','推荐商家','回购']):
            r = await get_top_merchants(user_id=user_id, window=90, top_k=5)
            return { 'cards': [
                { 'type':'recommendation', 'title':'好商家推荐', 'items': r.get('data',[]) }
            ]}
        # 预警（预算/大额）
        if any(k in q for k in ['预警','超额','大额']):
            bills = get_bills_simple(user_id=user_id, limit=1000)
            large = [b for b in bills if float(b.get('amount') or 0) >= 1000]
            return { 'cards': [
                { 'type':'alert', 'title':'大额支出提示', 'content': f"近记录中大额(≥1000) {len(large)} 笔"}
            ]}
        # 默认
        return { 'cards': [ { 'type':'tip', 'title':'试试这些', 'content':'“今日消费分析 / 消费趋势分析 / 好商家推荐 / 消费预警”' } ] }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成建议失败: {str(e)}")

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

# 预算管理API
class BudgetCreate(BaseModel):
    category: Optional[str] = None
    monthly_budget: float
    alert_threshold: Optional[float] = 0.8

@app.post(f"{API_V1_PREFIX}/budgets")
async def create_budget(budget: BudgetCreate, user_id: int = 1):
    """创建预算"""
    try:
        from .models import UserBudget
        budget_data = {
            'user_id': user_id,
            'category': budget.category,
            'monthly_budget': budget.monthly_budget,
            'alert_threshold': budget.alert_threshold
        }
        budget_obj = db_manager.create_budget(budget_data)
        return {"success": True, "data": {"id": budget_obj.id, **budget_data}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建预算失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/budgets")
async def get_budgets(user_id: int = 1):
    """获取用户预算列表"""
    try:
        budgets = db_manager.get_budgets(user_id)
        return {"success": True, "data": [{
            "id": b.id,
            "category": b.category,
            "monthly_budget": b.monthly_budget,
            "current_spent": b.current_spent,
            "alert_threshold": b.alert_threshold,
            "usage_ratio": b.current_spent / b.monthly_budget if b.monthly_budget > 0 else 0
        } for b in budgets]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预算失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/budgets/alerts")
async def get_budget_alerts(user_id: int = 1):
    """获取预算预警"""
    try:
        alerts = db_manager.get_budget_alerts(user_id)
        return {"success": True, "data": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预算预警失败: {str(e)}")

# 大额交易检测API
@app.get(f"{API_V1_PREFIX}/alerts/large-transactions")
async def get_large_transactions(user_id: int = 1, threshold: float = 1000.0):
    """获取大额交易（反欺诈提示）"""
    try:
        bills = get_bills_simple(user_id, limit=1000)
        large = [b for b in bills if float(b.get('amount', 0)) >= threshold]
        return {
            "success": True,
            "data": large[:20],
            "total": len(large),
            "threshold": threshold,
            "hints": {
                "fraud_risk": "大额交易已标记，建议核对商家信息",
                "frequency": f"近记录中发现 {len(large)} 笔大额交易"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取大额交易失败: {str(e)}")

# 社区帖子API
class PostCreate(BaseModel):
    title: str
    content: str
    bill_id: Optional[int] = None
    invoice_id: Optional[int] = None

@app.post(f"{API_V1_PREFIX}/community/posts")
async def create_post(post: PostCreate, user_id: int = 1):
    """创建社区帖子"""
    try:
        post_data = {
            'user_id': user_id,
            'title': post.title,
            'content': post.content,
            'bill_id': post.bill_id,
            'invoice_id': post.invoice_id
        }
        post_obj = db_manager.create_post(post_data)
        return {"success": True, "data": {"id": post_obj.id, **post_data}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建帖子失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/community/posts")
async def get_posts(limit: int = 20, offset: int = 0):
    """获取社区帖子列表"""
    try:
        posts = db_manager.get_posts(limit, offset)
        return {"success": True, "data": [{
            "id": p.id,
            "user_id": p.user_id,
            "title": p.title,
            "content": p.content,
            "bill_id": p.bill_id,
            "invoice_id": p.invoice_id,
            "likes_count": p.likes_count,
            "comments_count": p.comments_count,
            "created_at": p.created_at.isoformat() if hasattr(p.created_at, 'isoformat') else str(p.created_at)
        } for p in posts]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取帖子失败: {str(e)}")

@app.post(f"{API_V1_PREFIX}/community/posts/{{post_id}}/like")
async def like_post(post_id: int, user_id: int = 1):
    """点赞帖子"""
    try:
        success = db_manager.like_post(post_id, user_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"点赞失败: {str(e)}")

class CommentCreate(BaseModel):
    content: str

@app.post(f"{API_V1_PREFIX}/community/posts/{{post_id}}/comments")
async def create_comment(post_id: int, comment: CommentCreate, user_id: int = 1):
    """创建评论"""
    try:
        comment_data = {
            'post_id': post_id,
            'user_id': user_id,
            'content': comment.content
        }
        comment_obj = db_manager.create_comment(comment_data)
        return {"success": True, "data": {"id": comment_obj.id, **comment_data}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建评论失败: {str(e)}")

# 认证API（简化令牌）
class LoginRequest(BaseModel):
    username: str
    password: str = "demo"  # 演示环境简化

@app.post(f"{API_V1_PREFIX}/auth/login")
async def login(request: LoginRequest):
    """登录（演示环境简化认证）"""
    try:
        # 简化令牌生成
        import hashlib
        token = hashlib.md5(f"{request.username}:{datetime.now().isoformat()}".encode()).hexdigest()
        user_id = hash(request.username) % 1000 + 1  # 演示用户ID
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_id,
                "username": request.username
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@app.get(f"{API_V1_PREFIX}/auth/me")
async def get_current_user(token: str = None):
    """获取当前用户信息"""
    try:
        # 演示环境返回默认用户
        return {
            "success": True,
            "user": {
                "id": 1,
                "username": "demo_user",
                "email": "demo@example.com"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

# 深度学习预测API
@app.post(f"{API_V1_PREFIX}/ai/predict/totals")
async def predict_totals(user_id: int = 1, days: int = 30):
    """预测未来消费总额"""
    try:
        # 简化预测（实际应使用深度学习模型）
        bills = get_bills_simple(user_id, limit=100)
        avg_daily = sum(float(b.get('amount', 0)) for b in bills) / max(len(bills), 1) if bills else 0
        predicted = avg_daily * days
        
        return {
            "success": True,
            "data": {
                "predicted_total": round(predicted, 2),
                "period_days": days,
                "method": "moving_average",
                "confidence": 0.75
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

@app.post(f"{API_V1_PREFIX}/ai/predict/category")
async def predict_category(user_id: int = 1, days: int = 30):
    """预测各类别消费占比"""
    try:
        from collections import Counter
        bills = get_bills_simple(user_id, limit=1000)
        categories = Counter([b.get('category', '未知') for b in bills])
        total = sum(categories.values())
        predicted = {k: round(v/total * days, 0) if total > 0 else 0 for k, v in categories.items()}
        
        return {
            "success": True,
            "data": {
                "predicted_categories": predicted,
                "period_days": days,
                "method": "frequency_based"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"类别预测失败: {str(e)}")

@app.post(f"{API_V1_PREFIX}/ai/predict/merchant")
async def predict_merchant(user_id: int = 1, days: int = 30):
    """预测商家消费"""
    try:
        from collections import Counter
        bills = get_bills_simple(user_id, limit=1000)
        merchants = Counter([b.get('merchant', '未知') for b in bills])
        top_merchants = dict(merchants.most_common(5))
        
        return {
            "success": True,
            "data": {
                "predicted_merchants": top_merchants,
                "period_days": days,
                "method": "frequency_based"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"商家预测失败: {str(e)}")

@app.post(f"{API_V1_PREFIX}/ai/predict/anomaly")
async def predict_anomaly(user_id: int = 1):
    """异常检测"""
    try:
        bills = get_bills_simple(user_id, limit=1000)
        amounts = [float(b.get('amount', 0)) for b in bills if b.get('amount')]
        if not amounts:
            return {"success": True, "data": {"anomalies": [], "risk_score": 0.0}}
        
        import numpy as np
        mean, std = np.mean(amounts), np.std(amounts)
        threshold = mean + 2 * std
        anomalies = [b for b in bills if float(b.get('amount', 0)) > threshold]
        
        return {
            "success": True,
            "data": {
                "anomalies": anomalies[:10],
                "risk_score": min(len(anomalies) / len(bills) if bills else 0, 1.0),
                "threshold": round(threshold, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"异常检测失败: {str(e)}")

# 增强金融推荐（原因+风险）
@app.get(f"{API_V1_PREFIX}/ai/recommendations/financial/enhanced/{{user_id}}")
async def get_enhanced_financial_recommendations(user_id: int):
    """获取增强金融产品推荐（含原因和风险提示）"""
    try:
        recommendations = recommendation_engine.get_financial_recommendations(user_id)
        enhanced = []
        for rec in recommendations.get('recommendations', [])[:5]:
            enhanced.append({
                **rec,
                "why_recommend": {
                    "rules": ["基于您的消费能力匹配", "符合您的风险偏好"],
                    "feature_contributions": {
                        "spending_amount": "月度消费5000+，适合稳健理财",
                        "risk_tolerance": "低风险偏好，推荐保本产品"
                    }
                },
                "risk_warnings": {
                    "level": rec.get('risk_level', 'medium'),
                    "notes": "投资有风险，请根据自身情况谨慎选择",
                    "disclaimer": "本推荐仅供参考，不构成投资建议"
                }
            })
        
        return {
            "success": True,
            "data": {
                "recommendations": enhanced,
                "generated_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取增强推荐失败: {str(e)}")

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
