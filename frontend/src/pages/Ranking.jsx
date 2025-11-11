import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Select, Input, Tag, Spin, Empty, Pagination, Image, Rate, Button, Space, message } from 'antd'
import { EnvironmentOutlined, EyeOutlined, StarOutlined, FireOutlined, TrophyOutlined } from '@ant-design/icons'
import api from '../utils/api'
import { useNavigate } from 'react-router-dom'

const { Option } = Select
const { Search } = Input

function RankingPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [hotRankings, setHotRankings] = useState([])
  const [sponsorRankings, setSponsorRankings] = useState([])
  const [category, setCategory] = useState('')
  const [amountRange, setAmountRange] = useState('')
  const [sponsorPage, setSponsorPage] = useState(1)
  const [sponsorTotal, setSponsorTotal] = useState(0)

  useEffect(() => {
    loadRankings()
  }, [category, amountRange])

  useEffect(() => {
    loadSponsorRankings()
  }, [sponsorPage])

  const loadRankings = async () => {
    setLoading(true)
    try {
      const params = {
        limit: 50
      }
      if (category) params.category = category
      if (amountRange) {
        const [min, max] = amountRange.split('-').map(v => parseFloat(v))
        if (!isNaN(min)) params.amount_min = min
        if (!isNaN(max)) params.amount_max = max
      }

      const res = await api.get('/rankings/hot', { params })
      if (res.success) {
        setHotRankings(res.data || [])
      }
    } catch (error) {
      message.error('加载热门榜单失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadSponsorRankings = async () => {
    try {
      const res = await api.get('/rankings/sponsor', { 
        params: { page: sponsorPage, page_size: 10 } 
      })
      if (res.success) {
        setSponsorRankings(res.data || [])
        if (res.pagination) {
          setSponsorTotal(res.pagination.total)
        }
      }
    } catch (error) {
      message.error('加载赞助榜单失败')
      console.error(error)
    }
  }

  const handleMerchantClick = async (merchantId, clickType = 'view') => {
    try {
      await api.post(`/merchants/${merchantId}/click`, null, {
        params: { click_type: clickType }
      })
    } catch (error) {
      // 静默失败，不影响用户体验
      console.error('记录点击失败:', error)
    }
  }

  const handleViewDetail = (merchantId) => {
    handleMerchantClick(merchantId, 'detail')
    navigate(`/merchants/${merchantId}`)
  }

  const categories = ['全部', '餐饮', '交通', '购物', '娱乐', '医疗', '教育', '其他']
  const amountRanges = [
    { label: '全部', value: '' },
    { label: '0-50元', value: '0-50' },
    { label: '50-100元', value: '50-100' },
    { label: '100-200元', value: '100-200' },
    { label: '200元以上', value: '200-999999' }
  ]

  return (
    <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 'bold', marginBottom: 16 }}>
          <FireOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
          热门商家榜单
        </h1>
        <Space wrap>
          <Select
            style={{ width: 120 }}
            placeholder="选择类别"
            value={category}
            onChange={setCategory}
            allowClear
          >
            {categories.map(cat => (
              <Option key={cat} value={cat === '全部' ? '' : cat}>{cat}</Option>
            ))}
          </Select>
          <Select
            style={{ width: 150 }}
            placeholder="选择金额区间"
            value={amountRange}
            onChange={setAmountRange}
            allowClear
          >
            {amountRanges.map(range => (
              <Option key={range.value} value={range.value}>{range.label}</Option>
            ))}
          </Select>
          <Button onClick={loadRankings}>刷新</Button>
        </Space>
      </div>

      <Row gutter={16}>
        {/* 左侧：热门商家（61.8%宽度，黄金分割比） */}
        <Col xs={24} lg={15} style={{ marginBottom: 16 }}>
          <Card 
            title={
              <span>
                <TrophyOutlined style={{ color: '#faad14', marginRight: 8 }} />
                热门商家排行
              </span>
            }
            loading={loading}
          >
            {hotRankings.length === 0 ? (
              <Empty description="暂无热门商家" />
            ) : (
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                {hotRankings.map((merchant, index) => (
                  <Card
                    key={merchant.merchant_id}
                    hoverable
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleViewDetail(merchant.merchant_id)}
                    bodyStyle={{ padding: 16 }}
                  >
                    <Row align="middle" gutter={16}>
                      <Col span={2}>
                        <div style={{
                          width: 40,
                          height: 40,
                          borderRadius: 8,
                          background: index < 3 ? '#ff4d4f' : '#1890ff',
                          color: 'white',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 18,
                          fontWeight: 'bold'
                        }}>
                          {index + 1}
                        </div>
                      </Col>
                      <Col span={6}>
                        {merchant.images && merchant.images.length > 0 ? (
                          <Image
                            src={merchant.images[0]}
                            alt={merchant.merchant_name}
                            width={80}
                            height={80}
                            style={{ objectFit: 'cover', borderRadius: 8 }}
                            preview={false}
                          />
                        ) : (
                          <div style={{
                            width: 80,
                            height: 80,
                            background: '#f0f0f0',
                            borderRadius: 8,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#999'
                          }}>
                            暂无图片
                          </div>
                        )}
                      </Col>
                      <Col span={16}>
                        <div style={{ marginBottom: 8 }}>
                          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 'bold' }}>
                            {merchant.merchant_name}
                          </h3>
                          <Space size="small" style={{ marginTop: 4 }}>
                            <Tag color="blue">{merchant.category}</Tag>
                            {merchant.avg_rating > 0 && (
                              <span>
                                <Rate disabled value={merchant.avg_rating} allowHalf style={{ fontSize: 12 }} />
                                <span style={{ marginLeft: 4, color: '#999', fontSize: 12 }}>
                                  {merchant.avg_rating} ({merchant.review_count})
                                </span>
                              </span>
                            )}
                          </Space>
                        </div>
                        <div style={{ color: '#666', fontSize: 14 }}>
                          <div>消费次数: <strong>{merchant.consumption_count}</strong> 次</div>
                          <div>消费总额: <strong style={{ color: '#ff4d4f' }}>¥{merchant.consumption_amount.toFixed(2)}</strong></div>
                        </div>
                      </Col>
                    </Row>
                  </Card>
                ))}
              </Space>
            )}
          </Card>
        </Col>

        {/* 右侧：赞助商家（38.2%宽度） */}
        <Col xs={24} lg={9}>
          <Card 
            title={
              <span>
                <StarOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
                赞助商家推荐
              </span>
            }
          >
            {sponsorRankings.length === 0 ? (
              <Empty description="暂无赞助商家" size="small" />
            ) : (
              <Space direction="vertical" style={{ width: '100%' }} size="small">
                {sponsorRankings.map((sponsor) => (
                  <Card
                    key={sponsor.sponsorship_id}
                    size="small"
                    hoverable
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleViewDetail(sponsor.merchant_id)}
                    bodyStyle={{ padding: 12 }}
                  >
                    <Row align="middle" gutter={8}>
                      <Col span={8}>
                        {sponsor.images && sponsor.images.length > 0 ? (
                          <Image
                            src={sponsor.images[0]}
                            alt={sponsor.merchant_name}
                            width={60}
                            height={60}
                            style={{ objectFit: 'cover', borderRadius: 4 }}
                            preview={false}
                          />
                        ) : (
                          <div style={{
                            width: 60,
                            height: 60,
                            background: '#f0f0f0',
                            borderRadius: 4,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 10,
                            color: '#999'
                          }}>
                            暂无图片
                          </div>
                        )}
                      </Col>
                      <Col span={16}>
                        <div style={{ fontSize: 14, fontWeight: 'bold', marginBottom: 4 }}>
                          {sponsor.merchant_name}
                        </div>
                        <Tag size="small" color="orange">{sponsor.category}</Tag>
                        {sponsor.avg_rating > 0 && (
                          <div style={{ marginTop: 4 }}>
                            <Rate disabled value={sponsor.avg_rating} allowHalf style={{ fontSize: 10 }} />
                            <span style={{ fontSize: 10, color: '#999', marginLeft: 4 }}>
                              {sponsor.avg_rating}
                            </span>
                          </div>
                        )}
                        <div style={{ fontSize: 11, color: '#999', marginTop: 4 }}>
                          <EyeOutlined /> {sponsor.total_spent > 0 ? `已投入 ¥${sponsor.total_spent.toFixed(2)}` : '新入驻'}
                        </div>
                      </Col>
                    </Row>
                  </Card>
                ))}
              </Space>
            )}
            {sponsorTotal > 10 && (
              <div style={{ marginTop: 16, textAlign: 'center' }}>
                <Pagination
                  current={sponsorPage}
                  total={sponsorTotal}
                  pageSize={10}
                  onChange={setSponsorPage}
                  size="small"
                  showTotal={(total) => `共 ${total} 家赞助商家`}
                />
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default RankingPage

