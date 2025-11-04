import React, { useEffect, useMemo, useState } from 'react'
import { Card, Space, Segmented, Button, Modal, Alert, message, Row, Col, Tabs, Spin } from 'antd'
import { Column, Line, Pie, Radar } from '@ant-design/charts'
import api from '../utils/api'
import { getCurrentCity, getCurrentUserId, setCurrentCity } from '../utils/session'
import dayjs from 'dayjs'

function Assistant() {
  const [period, setPeriod] = useState('month') // day/month/year/all
  const [insight, setInsight] = useState(null)
  const [joinModal, setJoinModal] = useState(false)
  const [city] = useState(getCurrentCity())
  const [loading, setLoading] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)
  const [categoryData, setCategoryData] = useState([])
  const [trendData, setTrendData] = useState([])

  const userId = useMemo(() => getCurrentUserId(), [])

  useEffect(() => {
    loadData()
  }, [userId, city, period])

  const loadData = async () => {
    setLoading(true)
    try {
      // 加载洞察
      const ins = await api.get('/insight/dining-bias', { params: { user_id: userId, city } })
      setInsight(ins.data || ins)
      if ((ins.data?.trigger ?? ins.trigger) === true) {
        setJoinModal(true)
      }

      // 加载分析数据
      const summaryRes = await api.get('/analysis/summary', { params: { user_id: userId } })
      setAnalysisData(summaryRes.data || summaryRes)

      // 加载分类分析
      const categoryRes = await api.get('/analysis/category', { params: { user_id: userId } })
      const category = categoryRes.data || categoryRes || {}
      const catList = Object.entries(category).map(([k, v]) => ({
        category: k,
        amount: typeof v === 'number' ? v : parseFloat(v) || 0
      })).filter(x => x.amount > 0)
      setCategoryData(catList)

      // 加载趋势分析（按period）
      const trendRes = await api.get('/analysis/trend', { params: { user_id: userId, period } })
      const trend = trendRes.data || trendRes || {}
      const trendList = Object.entries(trend).map(([k, v]) => ({
        period: k,
        amount: typeof v === 'number' ? v : parseFloat(v) || 0
      })).filter(x => x.amount > 0)
      setTrendData(trendList)
    } catch (e) {
      console.error('加载数据失败:', e)
    } finally {
      setLoading(false)
    }
  }

  const timelineLabel = useMemo(() => ({
    day: '日', month: '月', year: '年', all: '全部'
  }[period]), [period])

  const columnConfig = {
    data: categoryData,
    xField: 'category',
    yField: 'amount',
    color: '#E02020',
    height: 300,
  }

  const lineConfig = {
    data: trendData,
    xField: 'period',
    yField: 'amount',
    smooth: true,
    color: '#1890ff',
    height: 300,
  }

  const pieConfig = {
    data: categoryData,
    angleField: 'amount',
    colorField: 'category',
    radius: 0.8,
    label: { type: 'outer' },
    height: 300,
  }

  const radarConfig = {
    data: categoryData.map(c => ({
      item: c.category,
      value: Math.min(100, (c.amount / (categoryData.reduce((sum, x) => sum + x.amount, 0) / categoryData.length)) * 10)
    })),
    xField: 'item',
    yField: 'value',
    area: {},
    point: { size: 5 },
    height: 300,
  }

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>账单小助手</h1>
          <Space>
            <Segmented
              options={[{label:'日', value:'day'},{label:'月', value:'month'},{label:'年', value:'year'},{label:'全部', value:'all'}]}
              value={period}
              onChange={setPeriod}
            />
            <Button onClick={async () => {
              try {
                const ins = await api.get('/insight/dining-bias', { params: { user_id: userId, city } })
                setInsight(ins.data || ins)
                if ((ins.data?.trigger ?? ins.trigger) === true) setJoinModal(true)
                else message.info('当前未触发餐饮偏好阈值')
              } catch {
                message.error('检测失败')
              }
            }}>重新检测弹窗</Button>
            <Button type="dashed" onClick={() => setJoinModal(true)}>测试弹窗</Button>
          </Space>
        </div>

        {/* 消费分析部分 */}
        <Card title={`时间线分析（${timelineLabel}）`}>
          {loading ? (
            <Spin />
          ) : (
            <Tabs
              items={[
                {
                  key: 'category',
                  label: '分类分析',
                  children: (
                    <Row gutter={[16, 16]}>
                      <Col xs={24} lg={14}>
                        <Card title="分类消费柱状图" style={{ height: 400 }}>
                          {categoryData.length > 0 ? (
                            <Column {...columnConfig} />
                          ) : (
                            <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>暂无数据</div>
                          )}
                        </Card>
                      </Col>
                      <Col xs={24} lg={10}>
                        <Card title="分类占比" style={{ height: 400 }}>
                          {categoryData.length > 0 ? (
                            <Pie {...pieConfig} />
                          ) : (
                            <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>暂无数据</div>
                          )}
                        </Card>
                      </Col>
                    </Row>
                  ),
                },
                {
                  key: 'trend',
                  label: '趋势分析',
                  children: (
                    <Card title={`消费趋势图（${timelineLabel}）`} style={{ height: 500 }}>
                      {trendData.length > 0 ? (
                        <Line {...lineConfig} />
                      ) : (
                        <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>暂无数据</div>
                      )}
                    </Card>
                  ),
                },
                {
                  key: 'radar',
                  label: '消费雷达图',
                  children: (
                    <Card title="消费分布雷达图" style={{ height: 500 }}>
                      {categoryData.length > 0 ? (
                        <Radar {...radarConfig} />
                      ) : (
                        <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>暂无数据</div>
                      )}
                    </Card>
                  ),
                },
              ]}
            />
          )}
        </Card>

        {/* 洞察与建议 */}
        <Card title="洞察与建议">
          {insight?.data?.trigger ? (
            <Alert type="info" showIcon message={`检测到餐饮偏好较强，建议加入 ${city} 餐饮群`} />
          ) : (
            <div style={{ color: '#999' }}>暂无强烈餐饮偏好。</div>
          )}
        </Card>

        {/* 汇总统计 */}
        {analysisData && (
          <Card title="汇总统计">
            <Row gutter={16}>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#E02020' }}>
                    ¥{parseFloat(analysisData.total_amount || 0).toFixed(2)}
                  </div>
                  <div style={{ color: '#999', marginTop: 4 }}>总消费</div>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                    {analysisData.total_count || 0}
                  </div>
                  <div style={{ color: '#999', marginTop: 4 }}>交易笔数</div>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>
                    ¥{parseFloat(analysisData.avg_amount || 0).toFixed(2)}
                  </div>
                  <div style={{ color: '#999', marginTop: 4 }}>平均金额</div>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#faad14' }}>
                    {categoryData.length || 0}
                  </div>
                  <div style={{ color: '#999', marginTop: 4 }}>消费类别</div>
                </div>
              </Col>
            </Row>
          </Card>
        )}
      </Space>

      <Modal
        open={joinModal}
        title={`加入${city}餐饮群？`}
        onCancel={() => setJoinModal(false)}
        footer={[
          <Button key="later" onClick={() => setJoinModal(false)}>稍后提醒</Button>,
          <Button key="no" onClick={() => setJoinModal(false)}>暂不加入</Button>,
          <Button key="ok" type="primary" onClick={async () => {
            try {
              const list = await api.get('/groups', { params: { city: city }})
              const target = (list.data || list).find?.(g => (g.name || '').includes('餐饮'))
              if (target?.id) {
                await api.post(`/groups/${target.id}/join`, null, { params: { user_id: userId } })
                message.success('已加入群组')
              }
            } catch {}
            setJoinModal(false)
          }}>加入</Button>
        ]}
      >
        <div style={{ marginBottom: 12 }}>是否记住当前城市选择？</div>
        <Space>
          <Button onClick={() => { setCurrentCity(city); message.success('已记住城市选择'); }}>记住当前城市</Button>
        </Space>
      </Modal>
    </div>
  )
}

export default Assistant
