import React, { useEffect, useMemo, useState } from 'react'
import PropTypes from 'prop-types'
import { Card, Space, Segmented, Button, Modal, Alert, message, Row, Col, Tabs, Spin, Progress, Statistic } from 'antd'
// 改用recharts替代@ant-design/charts，更稳定
import { BarChart, Bar, LineChart, Line, PieChart, Pie, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell, ResponsiveContainer } from 'recharts'
import api from '../utils/api'
import { getCurrentCity, getCurrentUserId, setCurrentCity } from '../utils/session'

// 图表颜色
const COLORS = ['#E02020', '#1890ff', '#52c41a', '#faad14', '#722ed1']

// 子组件：本月摘要卡
function SummaryCard({ summaryCard, anomalyCount }) {
  const getMomDisplay = (mom) => {
    if (mom == null) return '—'
    const absPercent = Math.round(Math.abs(mom) * 100)
    const arrow = mom >= 0 ? '↑' : '↓'
    return `${absPercent}% ${arrow}`
  }

  const getMomColor = (mom) => {
    if (mom == null) return '#999'
    return mom >= 0 ? '#E57373' : '#52c41a'
  }

  return (
    <Card>
      <Row gutter={16}>
        <Col xs={24} md={8}>
          <Statistic
            title="本月总消费"
            value={Number.parseFloat(summaryCard?.total || 0).toFixed(2)}
            prefix="¥"
            valueStyle={{ color: '#E02020', fontSize: 22, fontWeight: 700 }}
          />
        </Col>
        <Col xs={24} md={8}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: getMomColor(summaryCard?.mom) }}>
              {getMomDisplay(summaryCard?.mom)}
            </div>
            <div style={{ color: '#999', marginTop: 4 }}>较上月环比</div>
          </div>
        </Col>
        <Col xs={24} md={8}>
          <Statistic
            title="近30天异常次数"
            value={anomalyCount}
            valueStyle={{ color: anomalyCount > 0 ? '#faad14' : '#52c41a', fontSize: 20, fontWeight: 700 }}
          />
        </Col>
      </Row>
    </Card>
  )
}

SummaryCard.propTypes = {
  summaryCard: PropTypes.shape({
    total: PropTypes.number,
    mom: PropTypes.number,
  }),
  anomalyCount: PropTypes.number,
}

// 子组件：同类比对2.0卡片
function CohortV2Card({ cohortDim, setCohortDim, cohortV2, userId, onRefresh }) {
  const handleDimChange = async (v) => {
    setCohortDim(v)
    onRefresh(v)
  }

  const handleApplyBudget = async () => {
    try {
      const r = await api.post('/analytics/budget-optimize', { user_id: userId, min_saving_rate: 0.1 })
      const d = r.data?.data || r.data || r
      await api.post('/analytics/actions/apply-budget', { user_id: userId, suggestion: d.suggestion || {} })
      message.success('已应用预算建议')
    } catch {
      message.error('应用失败')
    }
  }

  const handleSetReminder = async () => {
    try {
      await api.post('/analytics/actions/set-reminder', { user_id: userId, type: 'budget_check', payload: { dim: cohortDim } })
      message.success('已设置提醒')
    } catch {
      message.error('设置失败')
    }
  }

  return (
    <Card title="同类比对 2.0">
      <Space style={{ marginBottom: 12 }}>
        <Segmented
          options={[{ label: '城市', value: 'city' }, { label: '年龄段', value: 'age' }, { label: '职业', value: 'job' }]}
          value={cohortDim}
          onChange={handleDimChange}
        />
        <Button onClick={handleApplyBudget}>一键应用预算建议</Button>
        <Button onClick={handleSetReminder}>设置提醒</Button>
      </Space>
      {cohortV2?.dimension ? (
        <>
          <div style={{ color: '#666', marginBottom: 8 }}>
            窗口：{cohortV2.window_days} 天；维度：{cohortV2.dimension}
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={(cohortV2.items || []).map(it => ({
              category: it.category,
              value: Math.round((it.relative_exposure || 0) * 100)
            }))} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis label={{ value: '相对暴露(%)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {(cohortV2.items || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={(entry.relative_exposure || 0) >= 0 ? '#E57373' : '#52c41a'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ marginTop: 8, color: '#999' }}>
            提示：红色代表该类别消费占比高于同类，绿色代表低于同类；可据此调整预算或设置提醒。
          </div>
        </>
      ) : (
        <div style={{ color: '#999' }}>暂无对比数据</div>
      )}
    </Card>
  )
}

CohortV2Card.propTypes = {
  cohortDim: PropTypes.string.isRequired,
  setCohortDim: PropTypes.func.isRequired,
  cohortV2: PropTypes.shape({
    data: PropTypes.shape({
      window_days: PropTypes.number,
      dimension: PropTypes.string,
      items: PropTypes.arrayOf(PropTypes.shape({
        category: PropTypes.string,
        relative_exposure: PropTypes.number,
      })),
    }),
  }),
  userId: PropTypes.number.isRequired,
  onRefresh: PropTypes.func.isRequired,
}

function Assistant() {
  const [period, setPeriod] = useState('month')
  const [insight, setInsight] = useState(null)
  const [joinModal, setJoinModal] = useState(false)
  const [city] = useState(getCurrentCity())
  const [loading, setLoading] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)
  const [categoryData, setCategoryData] = useState([])
  const [trendData, setTrendData] = useState([])
  const [health, setHealth] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [cohort, setCohort] = useState(null)
  const [cohortV2, setCohortV2] = useState(null)
  const [cohortDim, setCohortDim] = useState('city')
  const [summaryCard, setSummaryCard] = useState(null)
  const [anomalyCount, setAnomalyCount] = useState(0)
const INSIGHT_MEMORY_KEY = 'assistant_join_modal_shown'
  const isDark = (() => { try { return localStorage.getItem('pref_dark_mode') === '1' } catch { return false } })()

  const userId = useMemo(() => getCurrentUserId(), [])
const [insightShown, setInsightShown] = useState(() => {
  try {
    return sessionStorage.getItem(INSIGHT_MEMORY_KEY) === '1'
  } catch {
    return false
  }
})

const markInsightShown = () => {
  setInsightShown(true)
  try {
    sessionStorage.setItem(INSIGHT_MEMORY_KEY, '1')
  } catch {}
}

const openJoinModal = (mark = true) => {
  if (mark && !insightShown) {
    markInsightShown()
  }
  setJoinModal(true)
}

  useEffect(() => {
    loadData()
  }, [userId, city, period])

  // 拆分：加载基础分析数据
  const loadBasicAnalysis = async () => {
    const summaryRes = await api.get('/analysis/summary', { params: { user_id: userId } })
    setAnalysisData(summaryRes.data || summaryRes)

    const categoryRes = await api.get('/analysis/category', { params: { user_id: userId } })
    console.log('📊 Category API response:', categoryRes)
    const categoryData = categoryRes.data || categoryRes || {}
    console.log('📊 Category data:', categoryData)
    // 后端返回格式: {categories: {餐饮: {total_amount: xxx, ...}}}
    const categories = categoryData.categories || categoryData || {}
    const catList = Object.entries(categories).map(([k, v]) => ({
      category: k,
      amount: typeof v === 'number' ? v : (v.total_amount || Number.parseFloat(v) || 0)
    })).filter(x => x.amount > 0)
    console.log('📊 Category list:', catList)
    setCategoryData(catList)

    const trendRes = await api.get('/analysis/trend', { params: { user_id: userId, period } })
    const trendData = trendRes.data || trendRes || {}
    // 后端返回格式: {period: 'monthly', data: {2025-08: xxx, ...}}
    const trend = trendData.data || trendData || {}
    const trendList = Object.entries(trend).map(([k, v]) => ({
      period: k,
      amount: typeof v === 'number' ? v : Number.parseFloat(v) || 0
    })).filter(x => x.amount > 0)
    setTrendData(trendList)
    return trendList
  }

  // 拆分：加载高级分析（健康、预测、对比）
  const loadAdvancedAnalytics = async () => {
    try {
      const hs = await api.get('/analytics/health-score', { params: { user_id: userId } })
      const healthData = hs.data?.data || hs.data || hs
      setHealth(healthData)
    } catch (e) {
      console.error('健康评分加载失败:', e)
    }

    try {
      const fc = await api.get('/analytics/forecast', { params: { user_id: userId, period: 'month', horizon: 1 } })
      const forecastData = fc.data?.data || fc.data || fc
      setForecast(forecastData)
    } catch (e) {
      console.error('预测加载失败:', e)
    }

    try {
      const ct = await api.get('/analytics/cohort-compare', { params: { user_id: userId, dim: 'city' } })
      const cohortData = ct.data?.data || ct.data || ct
      setCohort(cohortData)
    } catch (e) {
      console.error('同类对比加载失败:', e)
    }

    try {
      const cv2 = await api.get('/analytics/cohort-compare/v2', { params: { user_id: userId, dim: cohortDim } })
      const cohortV2Data = cv2.data?.data || cv2.data || cv2
      setCohortV2(cohortV2Data)
    } catch (e) {
      console.error('同类对比v2加载失败:', e)
    }

    try {
      const an = await api.get('/analytics/anomaly', { params: { user_id: userId, window_days: 30 } })
      const arr = an.data?.data?.anomalies || an.data?.anomalies || []
      setAnomalyCount(Array.isArray(arr) ? arr.length : 0)
    } catch (e) {
      console.error('异常检测加载失败:', e)
    }
  }

  // 拆分：计算本月摘要
  const calculateSummary = (trendList) => {
    try {
      const arr = trendList || []
      if (arr.length >= 1) {
        const latest = arr.at(-1)
        const prev = arr.length >= 2 ? arr.at(-2) : null
        const total = latest.amount || 0
        const mom = prev?.amount ? ((total - prev.amount) / prev.amount) : null
        setSummaryCard({ total, mom })
      }
    } catch {}
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const ins = await api.get('/insight/dining-bias', { params: { user_id: userId, city } })
      const insightData = ins.data?.data || ins.data || ins
      setInsight(insightData)
      console.log('🍽️ Insight data:', insightData)
    if (insightData?.trigger === true && !insightShown) {
      openJoinModal()
      }

      const trendList = await loadBasicAnalysis()
      await loadAdvancedAnalytics()
      calculateSummary(trendList)
    } catch (e) {
      console.error('加载数据失败:', e)
    } finally {
      setLoading(false)
    }
  }

  const refreshCohortV2 = async (dim) => {
    try {
      const cv2 = await api.get('/analytics/cohort-compare/v2', { params: { user_id: userId, dim } })
      const cohortV2Data = cv2.data?.data || cv2.data || cv2
      setCohortV2(cohortV2Data)
    } catch (e) {
      console.error('同类比对v2刷新失败:', e)
    }
  }

  const timelineLabel = useMemo(() => ({
    day: '日', month: '月', year: '年', all: '全部'
  }[period]), [period])

  // Recharts的雷达图数据格式
  const radarData = useMemo(() => {
    if (!categoryData.length) return []
    const total = categoryData.reduce((sum, x) => sum + x.amount, 0)
    return categoryData.map(c => ({
      category: c.category,
      value: Math.round((c.amount / total) * 100) // 转换为百分比
    }))
  }, [categoryData])

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
                if ((ins.data?.trigger ?? ins.trigger) === true) {
                  openJoinModal(false)
                }
                else message.info('当前未触发餐饮偏好阈值')
              } catch {
                message.error('检测失败')
              }
            }}>重新检测弹窗</Button>
            <Button type="dashed" onClick={() => openJoinModal(false)}>测试弹窗</Button>
          </Space>
        </div>

        {/* 本月摘要卡 */}
        <SummaryCard summaryCard={summaryCard} anomalyCount={anomalyCount} />

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
                            <ResponsiveContainer width="100%" height={320}>
                              <BarChart data={categoryData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="category" />
                                <YAxis />
                                <Tooltip formatter={(value) => `¥${value.toFixed(2)}`} />
                                <Bar dataKey="amount" fill="#E02020" radius={[4, 4, 0, 0]} />
                              </BarChart>
                            </ResponsiveContainer>
                          ) : (
                            <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>暂无数据</div>
                          )}
                        </Card>
                      </Col>
                      <Col xs={24} lg={10}>
                        <Card title="分类占比" style={{ height: 400 }}>
                          {categoryData.length > 0 ? (
                            <ResponsiveContainer width="100%" height={320}>
                              <PieChart>
                                <Pie data={categoryData} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={80} label={(entry) => `${entry.category} ${((entry.amount / categoryData.reduce((s, x) => s + x.amount, 0)) * 100).toFixed(1)}%`}>
                                  {categoryData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                  ))}
                                </Pie>
                                <Tooltip formatter={(value) => `¥${value.toFixed(2)}`} />
                                <Legend />
                              </PieChart>
                            </ResponsiveContainer>
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
                        <ResponsiveContainer width="100%" height={420}>
                          <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="period" />
                            <YAxis />
                            <Tooltip formatter={(value) => `¥${value.toFixed(2)}`} />
                            <Legend />
                            <Line type="monotone" dataKey="amount" stroke="#1890ff" strokeWidth={2} dot={{ r: 4 }} name="消费金额" />
                          </LineChart>
                        </ResponsiveContainer>
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
                      {radarData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={420}>
                          <RadarChart data={radarData}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="category" />
                            <PolarRadiusAxis angle={90} domain={[0, 100]} />
                            <Radar name="占比%" dataKey="value" stroke="#E02020" fill="#E02020" fillOpacity={0.6} />
                            <Legend />
                            <Tooltip formatter={(value) => `${value}%`} />
                          </RadarChart>
                        </ResponsiveContainer>
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

        {/* 财务健康评分 */}
        <Card title="财务健康评分">
          {health?.score ? (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <Progress type="circle" percent={Math.min(100, Math.max(0, health.score || 0))} size={80} />
                <div style={{ color: '#666' }}>窗口：{health.window_days || 90} 天</div>
              </div>
              <Row gutter={16} style={{ marginTop: 12 }}>
                <Col xs={12} md={6}>收支平衡度：{Math.round((health.details?.balance || 0)*100)}%</Col>
                <Col xs={12} md={6}>稳定性：{Math.round((health.details?.stability || 0)*100)}%</Col>
                <Col xs={12} md={6}>预算达标：{Math.round((health.details?.budget || 0)*100)}%</Col>
                <Col xs={12} md={6}>异常健康：{Math.round((health.details?.anomaly || 0)*100)}%</Col>
              </Row>
            </>
          ) : (
            <div style={{ color: '#999' }}>暂无评分数据</div>
          )}
        </Card>

        {/* 预测与预算优化 */}
        <Card title="预测与预算">
          <Space direction="vertical" style={{ width: '100%' }}>
            {forecast?.forecast ? (
              <div style={{ color: '#666' }}>下月预测总支出：<strong>¥{(forecast.forecast?.[0] ?? 0).toFixed?.(2) || forecast.forecast?.[0] || 0}</strong>（方法：{forecast.method}）</div>
            ) : (
              <div style={{ color: '#999' }}>暂无预测数据</div>
            )}
            <Space>
              <Button onClick={async () => {
                try {
                  const r = await api.post('/analytics/budget-optimize', { user_id: userId, min_saving_rate: 0.1 })
                  const d = r.data?.data || r.data || r
                  const suggestion = d.suggestion || {}
                  Modal.confirm({
                    title: '预算建议',
                    width: 520,
                    okText: '应用预算',
                    cancelText: '仅查看',
                    content: (
                      <div>
                        <div style={{ marginBottom: 8 }}>最低储蓄：¥{(d.min_saving || 0).toFixed?.(2) || d.min_saving || 0}</div>
                        <pre style={{ background: '#f7f7f7', padding: 12, borderRadius: 6, maxHeight: 300, overflow: 'auto' }}>{JSON.stringify(suggestion, null, 2)}</pre>
                      </div>
                    ),
                    onOk: async () => {
                      try {
                        await api.post('/analytics/actions/apply-budget', { user_id: userId, suggestion })
                        message.success('预算建议已应用')
                        try {
                          window.dispatchEvent(new CustomEvent('budget-updated'))
                        } catch {}
                      } catch (err) {
                        console.error('应用预算失败:', err)
                        message.error('应用预算失败')
                        throw err
                      }
                    },
                  })
                } catch (err) {
                  console.error('预算优化失败:', err)
                  message.error('预算优化失败')
                }
              }}>一键生成预算建议</Button>
              <Button onClick={loadData}>刷新预测</Button>
            </Space>
          </Space>
        </Card>

        {/* 同类人群对比 */}
        <Card title="同类人群对比（按城市）">
          {cohort?.city ? (
            <>
              <div style={{ color: '#666', marginBottom: 8 }}>城市：{cohort.city || '—'}，窗口：{cohort.window_days} 天</div>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={(cohort.items || []).slice(0,8).map(it => ({ category: it.category, value: Math.round((it.diff_pct||0)*100) }))} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis label={{ value: '相对同类(%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#E02020" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </>
          ) : (
            <div style={{ color: '#999' }}>暂无对比数据</div>
          )}
        </Card>

        {/* 同类比对 2.0（城市/年龄/职业）*/}
        <CohortV2Card
          cohortDim={cohortDim}
          setCohortDim={setCohortDim}
          cohortV2={cohortV2}
          userId={userId}
          onRefresh={refreshCohortV2}
        />

        {/* 洞察与建议 */}
        <Card title="洞察与建议">
          {insight?.trigger ? (
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
                    ¥{Number.parseFloat(analysisData.total_amount || 0).toFixed(2)}
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
                    ¥{Number.parseFloat(analysisData.avg_amount || 0).toFixed(2)}
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

