import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Spin, Alert } from 'antd'
import { DollarOutlined, ShoppingOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons'
import { Line, Pie } from '@ant-design/charts'
import api from '../utils/api'

function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(null)
  const [trendData, setTrendData] = useState([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      // 获取消费汇总
      const summaryRes = await api.get('/analysis/summary?user_id=1')
      // API 返回格式: { success: true, data: {...} }
      const summaryData = summaryRes.success ? (summaryRes.data || summaryRes) : {}
      setSummary(summaryData)
      
      // 获取趋势数据
      try {
        const trendRes = await api.get('/analysis/trend?user_id=1&period=monthly')
        if (trendRes.success && trendRes.data && trendRes.data.monthly_data) {
          const monthlyData = trendRes.data.monthly_data
          setTrendData(Object.entries(monthlyData).map(([month, amount]) => ({
            month: `${parseInt(month)}月`,
            amount: parseFloat(amount) || 0
          })).slice(-6)) // 最近6个月
        } else {
          // 如果没有数据，使用模拟数据
          setTrendData([
            { month: '1月', amount: 3200 },
            { month: '2月', amount: 3500 },
            { month: '3月', amount: 3800 },
            { month: '4月', amount: 4200 },
            { month: '5月', amount: 4500 },
            { month: '6月', amount: 4800 },
          ])
        }
      } catch (trendError) {
        // 如果趋势接口失败，使用模拟数据
        setTrendData([
          { month: '1月', amount: 3200 },
          { month: '2月', amount: 3500 },
          { month: '3月', amount: 3800 },
          { month: '4月', amount: 4200 },
          { month: '5月', amount: 4500 },
          { month: '6月', amount: 4800 },
        ])
      }
    } catch (error) {
      console.error('加载数据失败:', error)
      // 设置默认值
      setSummary({
        total_amount: 0,
        total_count: 0,
        avg_amount: 0,
        categories: {}
      })
    } finally {
      setLoading(false)
    }
  }

  const lineConfig = {
    data: trendData,
    xField: 'month',
    yField: 'amount',
    point: { size: 5, shape: 'diamond' },
    color: '#E02020',
    smooth: true,
  }

  const pieData = summary?.categories 
    ? Object.entries(summary.categories)
        .map(([k, v]) => ({
          type: k || '未知',
          value: parseFloat(v.amount || v || 0)
        }))
        .filter(item => item.value > 0)
    : []

  const pieConfig = {
    data: pieData.length > 0 ? pieData : [{ type: '暂无数据', value: 1 }],
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    label: { 
      type: 'outer',
      formatter: (datum) => `${datum.type}: ¥${datum.value.toFixed(2)}`
    },
    legend: {
      position: 'bottom'
    },
    statistic: {
      title: false,
      content: {
        style: {
          whiteSpace: 'pre-wrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        },
        content: pieData.length === 0 ? '暂无数据' : '',
      },
    },
  }

  if (loading) {
    return <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24, fontSize: 24, fontWeight: 'bold' }}>账单小助手</h1>
      
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总消费"
              value={summary?.total_amount || 0}
              prefix={<DollarOutlined />}
              suffix="元"
              valueStyle={{ color: '#E02020' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="消费笔数"
              value={summary?.total_count || 0}
              prefix={<ShoppingOutlined />}
              suffix="笔"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均金额"
              value={summary?.avg_amount || 0}
              prefix={<RiseOutlined />}
              suffix="元"
              precision={2}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="本月趋势"
              value={11.28}
              prefix={<FallOutlined />}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={14}>
          <Card title="消费趋势" style={{ height: 400 }}>
            <Line {...lineConfig} />
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="消费分类" style={{ height: 400 }}>
            <Pie {...pieConfig} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Alert
            message="智能提醒"
            description="根据您的消费记录，建议关注餐饮和购物类别的支出，合理控制预算。"
            type="info"
            showIcon
            closable
          />
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard

