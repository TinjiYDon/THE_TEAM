"""
支付服务模块
集成微信支付和支付宝支付
"""
from datetime import datetime
from typing import Dict, Optional
import sqlite3
import uuid

try:
    from .config import PAYMENT_CONFIG, DATABASE_PATH
except ImportError:
    from config import PAYMENT_CONFIG, DATABASE_PATH


class PaymentService:
    """支付服务"""
    
    def __init__(self):
        self.config = PAYMENT_CONFIG
        self.db_path = DATABASE_PATH
    
    def create_wechat_payment(self, merchant_id: int, amount: float, 
                             sponsorship_id: Optional[int] = None,
                             description: str = "商家赞助费用") -> Dict:
        """创建微信支付订单
        
        Args:
            merchant_id: 商家ID
            amount: 支付金额
            sponsorship_id: 赞助记录ID（可选）
            description: 订单描述
        
        Returns:
            支付信息（包含支付URL、订单号等）
        """
        try:
            # 生成订单号
            order_no = f"WX{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            # 保存支付记录
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO merchant_payments
                (merchant_id, sponsorship_id, payment_type, amount, transaction_id, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'pending', datetime('now'))
            """, (merchant_id, sponsorship_id, 'wechat', amount, order_no))
            
            payment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # TODO: 调用微信支付API创建订单
            # 这里需要集成微信支付SDK
            # 示例代码（需要根据实际SDK调整）:
            """
            from wechatpay import WeChatPay
            
            wechat_pay = WeChatPay(
                app_id=self.config['wechat']['app_id'],
                mch_id=self.config['wechat']['mch_id'],
                api_key=self.config['wechat']['api_key']
            )
            
            payment_data = wechat_pay.create_order(
                out_trade_no=order_no,
                total_fee=int(amount * 100),  # 转换为分
                body=description,
                notify_url=self.config['wechat']['notify_url']
            )
            """
            
            # 返回支付信息（占位符）
            return {
                "success": True,
                "payment_id": payment_id,
                "order_no": order_no,
                "payment_type": "wechat",
                "amount": amount,
                "payment_url": f"https://pay.weixin.qq.com/order/{order_no}",  # 占位符
                "qr_code": f"data:image/png;base64,placeholder",  # 占位符
                "message": "请配置微信支付参数后使用"
            }
        except Exception as e:
            print(f"创建微信支付订单错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_alipay_payment(self, merchant_id: int, amount: float,
                             sponsorship_id: Optional[int] = None,
                             description: str = "商家赞助费用") -> Dict:
        """创建支付宝支付订单
        
        Args:
            merchant_id: 商家ID
            amount: 支付金额
            sponsorship_id: 赞助记录ID（可选）
            description: 订单描述
        
        Returns:
            支付信息（包含支付URL、订单号等）
        """
        try:
            # 生成订单号
            order_no = f"ALI{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            # 保存支付记录
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO merchant_payments
                (merchant_id, sponsorship_id, payment_type, amount, transaction_id, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'pending', datetime('now'))
            """, (merchant_id, sponsorship_id, 'alipay', amount, order_no))
            
            payment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # TODO: 调用支付宝API创建订单
            # 这里需要集成支付宝SDK
            # 示例代码（需要根据实际SDK调整）:
            """
            from alipay import AliPay
            
            alipay = AliPay(
                appid=self.config['alipay']['app_id'],
                app_private_key_string=self.config['alipay']['private_key'],
                alipay_public_key_string=self.config['alipay']['public_key']
            )
            
            order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=order_no,
                total_amount=str(amount),
                subject=description,
                return_url="https://example.com/return",
                notify_url=self.config['alipay']['notify_url']
            )
            """
            
            # 返回支付信息（占位符）
            return {
                "success": True,
                "payment_id": payment_id,
                "order_no": order_no,
                "payment_type": "alipay",
                "amount": amount,
                "payment_url": f"https://openapi.alipay.com/gateway.do?{order_no}",  # 占位符
                "message": "请配置支付宝支付参数后使用"
            }
        except Exception as e:
            print(f"创建支付宝支付订单错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_payment(self, payment_type: str, transaction_id: str) -> Dict:
        """验证支付结果
        
        Args:
            payment_type: 支付类型（wechat/alipay）
            transaction_id: 交易号
        
        Returns:
            验证结果
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM merchant_payments
                WHERE payment_type = ? AND transaction_id = ?
            """, (payment_type, transaction_id))
            
            payment = cursor.fetchone()
            if not payment:
                conn.close()
                return {
                    "success": False,
                    "error": "支付记录不存在"
                }
            
            # TODO: 调用支付平台API验证支付结果
            # 这里需要根据实际支付平台API进行验证
            
            # 更新支付状态（占位符）
            if payment['status'] == 'pending':
                cursor.execute("""
                    UPDATE merchant_payments
                    SET status = 'success', paid_at = datetime('now')
                    WHERE id = ?
                """, (payment['id'],))
                conn.commit()
            
            conn.close()
            
            return {
                "success": True,
                "payment_id": payment['id'],
                "status": payment['status'],
                "amount": payment['amount']
            }
        except Exception as e:
            print(f"验证支付错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_payment_notify(self, payment_type: str, notify_data: Dict) -> Dict:
        """处理支付回调通知
        
        Args:
            payment_type: 支付类型（wechat/alipay）
            notify_data: 回调数据
        
        Returns:
            处理结果
        """
        try:
            # TODO: 验证回调签名
            # 这里需要根据实际支付平台进行签名验证
            
            transaction_id = notify_data.get('transaction_id') or notify_data.get('out_trade_no')
            if not transaction_id:
                return {
                    "success": False,
                    "error": "缺少交易号"
                }
            
            # 更新支付状态
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE merchant_payments
                SET status = 'success', paid_at = datetime('now')
                WHERE transaction_id = ? AND status = 'pending'
            """, (transaction_id,))
            
            # 如果有关联的赞助记录，更新赞助状态
            cursor.execute("""
                SELECT sponsorship_id FROM merchant_payments
                WHERE transaction_id = ?
            """, (transaction_id,))
            
            payment_row = cursor.fetchone()
            if payment_row and payment_row[0]:
                sponsorship_id = payment_row[0]
                # 更新赞助记录状态为active
                cursor.execute("""
                    UPDATE merchant_sponsorships
                    SET status = 'active'
                    WHERE id = ? AND status = 'pending'
                """, (sponsorship_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "支付通知处理成功"
            }
        except Exception as e:
            print(f"处理支付通知错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# 全局实例
payment_service = PaymentService()
