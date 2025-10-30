import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Tag, Alert, Spin, Empty } from 'antd'
import { GiftOutlined, CheckCircleOutlined, WarningOutlined } from '@ant-design/icons'
import api from '../utils/api'

function Recommendations() {
  const [loading, setLoading] = useState(true)
  const [recommendations, setRecommendations] = useState([])

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    setLoading(true)
    try {
      const res = await api.get('/ai/recommendations/financial/enhanced/1')
      setRecommendations(res.data.recommendations || [])
    } catch (error) {
      console.error('加载推荐失败:', error)
      // 模拟数据
      setRecommendations([
        {
          product_name: '稳健理财A',
          product_type: '理财',
          interest_rate: 4.5,
          risk_level: 'low',
          why_recommend: {
            rules: ['基于您的消费能力匹配', '符合您的风险偏好'],
            feature_contributions: {
              spending_amount: '月度消费5000+，适合稳健理财',
              risk_tolerance: '低风险偏好，推荐保本产品',
            },
          },
          risk_warnings: {
            level: 'low',
            notes: '投资有风险，请根据自身情况谨慎选择',
            disclaimer: '本推荐仅供参考，不构成投资建议',
          },
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level) => {
    const colors = {
      low: 'green',
      medium: 'orange',
      high: 'red',
    }
    return colors[level] || 'default'
  }

  if (loading) {
    return <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24, fontSize: 24, fontWeight: 'bold' }}>金融产品推荐</h1>

      {recommendations.length === 0 ? (
        <Empty description="暂无推荐产品" />
      ) : (
        <Row gutter={[16, 16]}>
          {recommendations.map((rec, idx) => (
            <Col xs={24} lg={12} key={idx}>
              <Card
                title={
                  <Space>
                    <GiftOutlined style={{ color: '#E02020' }} />
                    <span>{rec.product_name}</span>
                    <Tag color={getRiskColor(rec.risk_level)}>{rec.risk_level === 'low' ? '低风险' : rec.risk_level === 'medium' ? '中风险' : '高风险'}</Tag>
                  </Space>
                }
                extra={<Tag color="blue">{rec.product_type}</Tag>}
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <strong>预期收益率：</strong>
                    <span style={{ fontSize: 20, color: '#E02020', fontWeight: 'bold' }}>
                      {rec.interest_rate}%
                    </span>
                  </div>

                  <div>
                    <strong>推荐理由：</strong>
                    <ul style={{ marginTop: 8 }}>
                      {rec.why_recommend?.rules?.map((rule, i) => (
                        <li key={i}>
                          <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                          {rule}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Alert
                    message="风险提示"
                    description={rec.risk_warnings?.notes}
                    type="warning"
                    icon={<WarningOutlined />}
                    showIcon
                  />
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  )
}

export default Recommendations

