import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Row, Col, Image, Rate, Tag, Button, Space, Spin, Empty, Descriptions, List, Avatar, Divider, message } from 'antd'
import { EnvironmentOutlined, PhoneOutlined, ClockCircleOutlined, LeftOutlined, NavigationOutlined, StarOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'

function MerchantDetailPage() {
  const { merchantId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [merchant, setMerchant] = useState(null)

  useEffect(() => {
    if (merchantId) {
      loadMerchantDetail()
      // 记录详情页访问
      trackClick('detail')
    }
  }, [merchantId])

  const loadMerchantDetail = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/merchants/${merchantId}`)
      if (res.success) {
        setMerchant(res.data)
      } else {
        message.error('获取商家详情失败')
      }
    } catch (error) {
      message.error('加载商家详情失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const trackClick = async (clickType) => {
    try {
      await api.post(`/merchants/${merchantId}/click`, null, {
        params: { click_type: clickType }
      })
    } catch (error) {
      console.error('记录点击失败:', error)
    }
  }

  const handleNavigate = () => {
    if (merchant?.latitude && merchant?.longitude) {
      trackClick('navigate')
      // 跳转到高德地图（预留接口）
      const amapUrl = `https://uri.amap.com/navigation?to=${merchant.longitude},${merchant.latitude}&toName=${encodeURIComponent(merchant.merchant_name || '')}&mode=car`
      window.open(amapUrl, '_blank')
    } else {
      message.warning('该商家暂无位置信息')
    }
  }

  if (loading) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!merchant) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="商家不存在" />
      </div>
    )
  }

  return (
    <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>
      <Button 
        icon={<LeftOutlined />} 
        onClick={() => navigate(-1)}
        style={{ marginBottom: 16 }}
      >
        返回
      </Button>

      <Card>
        <Row gutter={24}>
          {/* 左侧：商家图片和基本信息 */}
          <Col xs={24} md={10}>
            {merchant.images && merchant.images.length > 0 ? (
              <Image.PreviewGroup>
                <Image
                  src={merchant.images[0]}
                  alt={merchant.merchant_name}
                  style={{ width: '100%', borderRadius: 8, marginBottom: 16 }}
                />
                {merchant.images.length > 1 && (
                  <Row gutter={8}>
                    {merchant.images.slice(1, 5).map((img, index) => (
                      <Col span={6} key={index}>
                        <Image
                          src={img}
                          alt={`${merchant.merchant_name}-${index + 2}`}
                          style={{ width: '100%', borderRadius: 4 }}
                        />
                      </Col>
                    ))}
                  </Row>
                )}
              </Image.PreviewGroup>
            ) : (
              <div style={{
                width: '100%',
                height: 300,
                background: '#f0f0f0',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#999',
                marginBottom: 16
              }}>
                暂无图片
              </div>
            )}

            <Card size="small" style={{ marginTop: 16 }}>
              <Descriptions column={1} size="small">
                {merchant.phone && (
                  <Descriptions.Item label={<><PhoneOutlined /> 联系电话</>}>
                    {merchant.phone}
                  </Descriptions.Item>
                )}
                {merchant.business_hours && Object.keys(merchant.business_hours).length > 0 && (
                  <Descriptions.Item label={<><ClockCircleOutlined /> 营业时间</>}>
                    {JSON.stringify(merchant.business_hours)}
                  </Descriptions.Item>
                )}
              </Descriptions>
            </Card>
          </Col>

          {/* 右侧：商家详细信息 */}
          <Col xs={24} md={14}>
            <div style={{ marginBottom: 16 }}>
              <h1 style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 8 }}>
                {merchant.merchant_name}
              </h1>
              <Space size="middle" wrap>
                <Tag color="blue">{merchant.category}</Tag>
                {merchant.avg_rating > 0 && (
                  <span>
                    <Rate disabled value={merchant.avg_rating} allowHalf />
                    <span style={{ marginLeft: 8, fontSize: 16, fontWeight: 'bold' }}>
                      {merchant.avg_rating}
                    </span>
                    <span style={{ marginLeft: 4, color: '#999' }}>
                      ({merchant.review_count} 条评价)
                    </span>
                  </span>
                )}
              </Space>
            </div>

            {merchant.description && (
              <Card size="small" style={{ marginBottom: 16 }}>
                <h3>店铺说明</h3>
                <p style={{ color: '#666', lineHeight: 1.8 }}>{merchant.description}</p>
              </Card>
            )}

            {merchant.address && (
              <Card size="small" style={{ marginBottom: 16 }}>
                <Space>
                  <EnvironmentOutlined style={{ color: '#1890ff' }} />
                  <span>{merchant.address}</span>
                  {merchant.latitude && merchant.longitude && (
                    <Button
                      type="primary"
                      size="small"
                      icon={<NavigationOutlined />}
                      onClick={handleNavigate}
                    >
                      导航
                    </Button>
                  )}
                </Space>
              </Card>
            )}

            {merchant.click_stats && (
              <Card size="small" title="访问统计" style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 20, fontWeight: 'bold', color: '#1890ff' }}>
                        {merchant.click_stats.total_clicks || 0}
                      </div>
                      <div style={{ color: '#999', fontSize: 12 }}>总访问量</div>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 20, fontWeight: 'bold', color: '#52c41a' }}>
                        {merchant.click_stats.unique_visitors || 0}
                      </div>
                      <div style={{ color: '#999', fontSize: 12 }}>独立访客</div>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 20, fontWeight: 'bold', color: '#faad14' }}>
                        {merchant.click_stats.conversion_rate || 0}%
                      </div>
                      <div style={{ color: '#999', fontSize: 12 }}>转化率</div>
                    </div>
                  </Col>
                </Row>
              </Card>
            )}
          </Col>
        </Row>
      </Card>

      {/* 用户评价 */}
      {merchant.reviews && merchant.reviews.length > 0 && (
        <Card title={<><StarOutlined /> 用户评价 ({merchant.review_count})</>} style={{ marginTop: 16 }}>
          <List
            dataSource={merchant.reviews}
            renderItem={(review) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Avatar>{review.username?.[0] || 'U'}</Avatar>}
                  title={
                    <Space>
                      <span>{review.username || '匿名用户'}</span>
                      <Rate disabled value={review.rating} allowHalf style={{ fontSize: 12 }} />
                      <span style={{ color: '#999', fontSize: 12 }}>
                        {dayjs(review.created_at).format('YYYY-MM-DD HH:mm')}
                      </span>
                    </Space>
                  }
                  description={
                    <div>
                      {review.content && <p style={{ marginBottom: 8 }}>{review.content}</p>}
                      {review.images && review.images.length > 0 && (
                        <Image.PreviewGroup>
                          <Space>
                            {review.images.map((img, idx) => (
                              <Image
                                key={idx}
                                src={img}
                                width={60}
                                height={60}
                                style={{ objectFit: 'cover', borderRadius: 4 }}
                              />
                            ))}
                          </Space>
                        </Image.PreviewGroup>
                      )}
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  )
}

export default MerchantDetailPage

