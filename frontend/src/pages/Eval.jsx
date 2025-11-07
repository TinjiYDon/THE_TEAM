import React, { useEffect, useState } from 'react'
import { Card, Space, Alert, Button, Table } from 'antd'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Dot } from 'recharts'
import api from '../utils/api'
import { getCurrentUserId } from '../utils/session'

function EvalPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const userId = getCurrentUserId()

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.get('/analytics/eval', { params: { user_id: userId, period: 'month' } })
      const evalData = res.data?.data || res.data || res
      setData(evalData)
      console.log('📊 Eval data:', evalData)
    } catch (e) {
      console.error('评测数据加载失败:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const cols = [
    { title: '周期', dataIndex: 'period', key: 'period' },
    { title: '金额', dataIndex: 'amount', key: 'amount', render: (v) => `¥${Number.parseFloat(v || 0).toFixed(2)}` },
  ]

  const chartData = (data?.points || []).map(p => ({
    period: p.period,
    amount: p.amount,
    isAnomaly: data?.anomaly_threshold != null && p.amount > data.anomaly_threshold
  }))

  // 自定义点的渲染：异常点为红色
  const CustomDot = (props) => {
    const { cx, cy, payload } = props
    const color = payload.isAnomaly ? '#f5222d' : '#5B8FF9'
    return <Dot cx={cx} cy={cy} r={4} fill={color} stroke={color} />
  }

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>评测与实验</h1>
          <Space>
            <Button onClick={load} loading={loading}>刷新</Button>
          </Space>
        </div>

        {data?.period ? (
          <>
            <Card title="预测误差（MAPE）">
              <div>周期：{data.period}</div>
              <div>MAPE：{data.mape != null ? `${data.mape.toFixed ? data.mape.toFixed(2) : data.mape}%` : '—'}</div>
            </Card>
            <Card title="异常检测回测">
              <div>阈值：{data.anomaly_threshold != null ? `¥${data.anomaly_threshold}` : '—'}</div>
              <div>异常周期（近6）：{(data.anomaly_periods || []).join('、') || '—'}</div>
            </Card>
            <Card title="历史点（近12）">
              <div style={{ marginBottom: 12 }}>
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip formatter={(value) => `¥${value.toFixed(2)}`} />
                    <Legend />
                    <Line type="monotone" dataKey="amount" stroke="#5B8FF9" strokeWidth={2} dot={<CustomDot />} name="消费金额" />
                    {data.anomaly_threshold != null && (
                      <ReferenceLine y={data.anomaly_threshold} stroke="#faad14" strokeDasharray="4 4" label="异常阈值" />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <Table columns={cols} dataSource={(data.points || []).map((x,i)=>({key:i,...x}))} size="small" pagination={false} />
            </Card>
          </>
        ) : (
          <Alert type="info" message="暂无评测数据" />
        )}
      </Space>
    </div>
  )
}

export default EvalPage


