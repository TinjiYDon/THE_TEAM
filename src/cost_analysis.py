"""
消费分析模块 - 数据分析和可视化
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import base64
from io import BytesIO

# 尝试导入seaborn，如果失败则跳过
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("Warning: seaborn not available, some visualization features may be limited")

from .database import db_manager
from .config import CHART_CONFIG

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CostAnalyzer:
    """消费分析器"""
    
    def __init__(self):
        self.config = CHART_CONFIG
        self.colors = self.config['default_colors']
    
    def get_spending_analysis(self, user_id: int, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """获取消费分析报告"""
        # 获取基础数据
        if start_date and end_date:
            bills = db_manager.get_bills_by_date_range(user_id, start_date, end_date)
        else:
            bills = db_manager.get_bills(user_id, limit=1000)
        
        if not bills:
            return {
                'summary': {'total_amount': 0, 'total_count': 0, 'avg_amount': 0},
                'charts': {},
                'insights': []
            }
        
        # 转换为DataFrame
        df = pd.DataFrame([{
            'id': bill.id,
            'consume_time': bill.consume_time,
            'amount': bill.amount,
            'merchant': bill.merchant,
            'category': bill.category,
            'payment_method': bill.payment_method
        } for bill in bills])
        
        # 基础统计
        summary = self._calculate_summary(df)
        
        # 生成图表
        charts = self._generate_charts(df)
        
        # 生成洞察
        insights = self._generate_insights(df)
        
        return {
            'summary': summary,
            'charts': charts,
            'insights': insights,
            'data_points': len(df)
        }
    
    def _calculate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算基础统计信息"""
        return {
            'total_amount': float(df['amount'].sum()),
            'total_count': len(df),
            'avg_amount': float(df['amount'].mean()),
            'max_amount': float(df['amount'].max()),
            'min_amount': float(df['amount'].min()),
            'median_amount': float(df['amount'].median()),
            'std_amount': float(df['amount'].std())
        }
    
    def _generate_charts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成各种图表"""
        charts = {}
        
        # 1. 消费类别饼图
        charts['category_pie'] = self._create_category_pie_chart(df)
        
        # 2. 月度消费趋势图
        charts['monthly_trend'] = self._create_monthly_trend_chart(df)
        
        # 3. 支付方式柱状图
        charts['payment_method_bar'] = self._create_payment_method_chart(df)
        
        # 4. 消费金额分布直方图
        charts['amount_distribution'] = self._create_amount_distribution_chart(df)
        
        # 5. 消费类别雷达图
        charts['category_radar'] = self._create_category_radar_chart(df)
        
        # 6. 消费漏斗图
        charts['spending_funnel'] = self._create_spending_funnel_chart(df)
        
        # 7. 消费箱线图
        charts['amount_boxplot'] = self._create_amount_boxplot_chart(df)
        
        return charts
    
    def _create_category_pie_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """创建消费类别饼图"""
        category_data = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[go.Pie(
            labels=category_data.index.tolist(),
            values=category_data.values.tolist(),
            hole=0.3,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title="消费类别分布",
            font=dict(size=12),
            showlegend=True
        )
        
        return {
            'type': 'pie',
            'data': fig.to_dict(),
            'title': '消费类别分布'
        }
    
    def _create_monthly_trend_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """创建月度消费趋势图"""
        df['month'] = df['consume_time'].dt.to_period('M')
        monthly_data = df.groupby('month')['amount'].sum().reset_index()
        monthly_data['month_str'] = monthly_data['month'].astype(str)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_data['month_str'],
            y=monthly_data['amount'],
            mode='lines+markers',
            name='月度消费',
            line=dict(color=self.colors[0], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="月度消费趋势",
            xaxis_title="月份",
            yaxis_title="消费金额 (元)",
            hovermode='x unified'
        )
        
        return {
            'type': 'line',
            'data': fig.to_dict(),
            'title': '月度消费趋势'
        }
    
    def _create_payment_method_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """创建支付方式柱状图"""
        payment_data = df.groupby('payment_method')['amount'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[
            go.Bar(
                x=payment_data.index.tolist(),
                y=payment_data.values.tolist(),
                marker_color=self.colors[:len(payment_data)]
            )
        ])
        
        fig.update_layout(
            title="支付方式统计",
            xaxis_title="支付方式",
            yaxis_title="消费金额 (元)"
        )
        
        return {
            'type': 'bar',
            'data': fig.to_dict(),
            'title': '支付方式统计'
        }
    
    def _create_amount_distribution_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """创建消费金额分布直方图"""
        fig = go.Figure(data=[
            go.Histogram(
                x=df['amount'],
                nbinsx=20,
                marker_color=self.colors[0],
                opacity=0.7
            )
        ])
        
        fig.update_layout(
            title="消费金额分布",
            xaxis_title="消费金额 (元)",
            yaxis_title="频次"
        )
        
        return {
            'type': 'histogram',
            'data': fig.to_dict(),
            'title': '消费金额分布'
        }
    
    def _create_category_radar_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """创建消费类别雷达图"""
        # 按类别统计消费金额
        category_data = df.groupby('category')['amount'].sum()
        
        # 创建雷达图数据
        categories = category_data.index.tolist()
        values = category_data.values.tolist()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='消费金额',
            line_color=self.colors[0]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values)]
                )),
            showlegend=True,
            title="消费类别雷达图"
        )
        
        return {
            'type': 'radar',
            'data': fig.to_dict(),
            'title': '消费类别雷达图'
        }
    
    def _create_spending_funnel_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """创建消费漏斗图"""
        # 按金额区间创建漏斗
        df['amount_range'] = pd.cut(df['amount'], 
                                  bins=[0, 50, 100, 200, 500, 1000, float('inf')],
                                  labels=['0-50', '50-100', '100-200', '200-500', '500-1000', '1000+'])
        
        funnel_data = df.groupby('amount_range').size().sort_values(ascending=False)
        
        fig = go.Figure(go.Funnel(
            y=funnel_data.index.tolist(),
            x=funnel_data.values.tolist(),
            textinfo="value+percent initial",
            marker=dict(color=self.colors)
        ))
        
        fig.update_layout(
            title="消费金额漏斗图",
            xaxis_title="消费笔数"
        )
        
        return {
            'type': 'funnel',
            'data': fig.to_dict(),
            'title': '消费金额漏斗图'
        }
    
    def _create_amount_boxplot_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """创建消费金额箱线图"""
        fig = go.Figure()
        
        # 按类别创建箱线图
        for category in df['category'].unique():
            category_data = df[df['category'] == category]['amount']
            fig.add_trace(go.Box(
                y=category_data,
                name=category,
                boxpoints='outliers'
            ))
        
        fig.update_layout(
            title="消费金额箱线图",
            yaxis_title="消费金额 (元)",
            xaxis_title="消费类别"
        )
        
        return {
            'type': 'box',
            'data': fig.to_dict(),
            'title': '消费金额箱线图'
        }
    
    def _generate_insights(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """生成消费洞察"""
        insights = []
        
        # 1. 消费总额洞察
        total_amount = df['amount'].sum()
        avg_amount = df['amount'].mean()
        
        if total_amount > 5000:
            insights.append({
                'type': 'high_spending',
                'title': '高消费提醒',
                'message': f'本月消费总额为{total_amount:.2f}元，建议合理控制支出',
                'level': 'warning'
            })
        
        # 2. 消费类别洞察
        category_data = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        top_category = category_data.index[0]
        top_amount = category_data.iloc[0]
        
        insights.append({
            'type': 'category_analysis',
            'title': '主要消费类别',
            'message': f'主要消费类别是{top_category}，占总消费的{top_amount/total_amount*100:.1f}%',
            'level': 'info'
        })
        
        # 3. 消费频率洞察
        daily_spending = df.groupby(df['consume_time'].dt.date)['amount'].sum()
        avg_daily = daily_spending.mean()
        
        if avg_daily > 200:
            insights.append({
                'type': 'frequency_analysis',
                'title': '消费频率分析',
                'message': f'平均每日消费{avg_daily:.2f}元，消费频率较高',
                'level': 'info'
            })
        
        # 4. 支付方式洞察
        payment_data = df.groupby('payment_method')['amount'].sum().sort_values(ascending=False)
        top_payment = payment_data.index[0]
        
        insights.append({
            'type': 'payment_analysis',
            'title': '支付方式偏好',
            'message': f'主要使用{top_payment}支付，占总消费的{payment_data.iloc[0]/total_amount*100:.1f}%',
            'level': 'info'
        })
        
        # 5. 消费趋势洞察
        df['date'] = df['consume_time'].dt.date
        daily_amounts = df.groupby('date')['amount'].sum()
        
        if len(daily_amounts) > 7:
            recent_trend = daily_amounts.tail(7).mean()
            earlier_trend = daily_amounts.head(7).mean()
            
            if recent_trend > earlier_trend * 1.2:
                insights.append({
                    'type': 'trend_analysis',
                    'title': '消费趋势上升',
                    'message': '最近7天消费比前7天增长了20%以上，请注意控制支出',
                    'level': 'warning'
                })
            elif recent_trend < earlier_trend * 0.8:
                insights.append({
                    'type': 'trend_analysis',
                    'title': '消费趋势下降',
                    'message': '最近7天消费比前7天下降了20%以上，消费控制良好',
                    'level': 'success'
                })
        
        return insights
    
    def get_category_analysis(self, user_id: int, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """获取分类消费分析"""
        if start_date and end_date:
            bills = db_manager.get_bills_by_date_range(user_id, start_date, end_date)
        else:
            bills = db_manager.get_bills(user_id, limit=1000)
        
        if not bills:
            return {'categories': [], 'total_amount': 0}
        
        df = pd.DataFrame([{
            'category': bill.category,
            'amount': bill.amount,
            'consume_time': bill.consume_time
        } for bill in bills])
        
        # 按类别统计
        category_stats = df.groupby('category').agg({
            'amount': ['sum', 'count', 'mean', 'std']
        }).round(2)
        
        category_stats.columns = ['total_amount', 'count', 'avg_amount', 'std_amount']
        category_stats = category_stats.sort_values('total_amount', ascending=False)
        
        # 计算占比
        total_amount = category_stats['total_amount'].sum()
        category_stats['percentage'] = (category_stats['total_amount'] / total_amount * 100).round(2)
        
        return {
            'categories': category_stats.to_dict('index'),
            'total_amount': total_amount,
            'category_count': len(category_stats)
        }
    
    def get_trend_analysis(self, user_id: int, period: str = 'monthly') -> Dict[str, Any]:
        """获取趋势分析"""
        if period == 'monthly':
            # 获取月度数据
            current_year = datetime.now().year
            monthly_data = db_manager.get_monthly_spending(user_id, current_year)
            
            return {
                'period': 'monthly',
                'data': monthly_data,
                'total_amount': sum(item['total_amount'] for item in monthly_data),
                'avg_monthly': sum(item['total_amount'] for item in monthly_data) / len(monthly_data) if monthly_data else 0
            }
        elif period == 'weekly':
            # 获取周度数据
            bills = db_manager.get_bills(user_id, limit=1000)
            if not bills:
                return {'period': 'weekly', 'data': [], 'total_amount': 0}
            
            df = pd.DataFrame([{
                'consume_time': bill.consume_time,
                'amount': bill.amount
            } for bill in bills])
            
            df['week'] = df['consume_time'].dt.to_period('W')
            weekly_data = df.groupby('week')['amount'].sum().reset_index()
            weekly_data['week_str'] = weekly_data['week'].astype(str)
            
            return {
                'period': 'weekly',
                'data': weekly_data.to_dict('records'),
                'total_amount': weekly_data['amount'].sum()
            }
        
        return {'period': period, 'data': [], 'total_amount': 0}
    
    def generate_report(self, user_id: int, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """生成完整的消费分析报告"""
        analysis = self.get_spending_analysis(user_id, start_date, end_date)
        category_analysis = self.get_category_analysis(user_id, start_date, end_date)
        trend_analysis = self.get_trend_analysis(user_id, 'monthly')
        
        return {
            'report_info': {
                'user_id': user_id,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'generated_at': datetime.now().isoformat()
            },
            'spending_analysis': analysis,
            'category_analysis': category_analysis,
            'trend_analysis': trend_analysis,
            'recommendations': self._generate_recommendations(analysis, category_analysis)
        }
    
    def _generate_recommendations(self, spending_analysis: Dict, category_analysis: Dict) -> List[Dict[str, Any]]:
        """生成消费建议"""
        recommendations = []
        
        summary = spending_analysis['summary']
        categories = category_analysis['categories']
        
        # 基于消费总额的建议
        if summary['total_amount'] > 10000:
            recommendations.append({
                'type': 'budget_control',
                'title': '预算控制建议',
                'message': '消费总额较高，建议制定月度预算并严格执行',
                'priority': 'high'
            })
        
        # 基于消费类别的建议
        if categories:
            top_category = max(categories.keys(), key=lambda k: categories[k]['total_amount'])
            top_percentage = categories[top_category]['percentage']
            
            if top_percentage > 50:
                recommendations.append({
                    'type': 'category_balance',
                    'title': '消费结构优化',
                    'message': f'{top_category}消费占比过高({top_percentage:.1f}%)，建议增加其他类别消费',
                    'priority': 'medium'
                })
        
        # 基于消费频率的建议
        if summary['total_count'] > 100:
            recommendations.append({
                'type': 'frequency_control',
                'title': '消费频率控制',
                'message': '消费频次较高，建议减少不必要的消费',
                'priority': 'medium'
            })
        
        return recommendations

# 创建全局分析器实例
cost_analyzer = CostAnalyzer()
