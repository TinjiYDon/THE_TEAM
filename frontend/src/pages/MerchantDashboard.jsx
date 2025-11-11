import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Button, Space, Spin, Empty, message, Modal, Form, InputNumber, Input } from 'antd'
import { EyeOutlined, UserOutlined, RiseOutlined, DollarOutlined, TrophyOutlined, PlusOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'

function MerchantDashboardPage() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [sponsorModalVisible, setSponsorModalVisible] = useState(false)
  const [sponsorForm] = Form.useForm()

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setLoading(true)
    try {
      const res = await api.get('/merchants/dashboard/stats')
      if (res.success) {
        setStats(res.data)
      } else {
        message.warning(res.message || '未认证商家')
      }
    } catch (error) {
      message.error('加载统计数据失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSponsorship = async (values) => {
    try {
      const res = await api.post('/merchants/sponsor', values)
      if (res.success) {
        message.success('赞助申请已创建，请完成支付')
        setSponsorModalVisible(false)
        sponsorForm.resetFields()
        loadStats()
        // TODO: 跳转到支付页面
      } else {
        message.error(res.detail || '创建赞助失败')
      }
    } catch (error) {
      message.error('创建赞助失败')
      console.error(error)
    }
  }

  if (loading) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!stats) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="请先完成商家认证" />
      </div>
    )
  }

  const clickStats = stats.click_stats || {}
  const sponsorship = stats.sponsorship

  return (
    <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 'bold' }}>商家后台管理</h1>
      </div>

      {/* 数据概览 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总访问量"
              value={clickStats.total_clicks || 0}
              prefix={<EyeOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="独立访客"
              value={clickStats.unique_visitors || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="转化率"
              value={stats.conversion_rate || 0}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总投入"
              value={sponsorship?.total_spent || 0}
              prefix={<DollarOutlined />}
              precision={2}
              suffix="元"
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 详细统计 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="访问统计详情">
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                    {clickStats.valid_clicks || 0}
                  </div>
                  <div style={{ color: '#999', marginTop: 8 }}>有效点击</div>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>
                    {clickStats.detail_views || 0}
                  </div>
                  <div style={{ color: '#999', marginTop: 8 }}>详情页访问</div>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#faad14' }}>
                    {clickStats.navigations || 0}
                  </div>
                  <div style={{ color: '#999', marginTop: 8 }}>导航次数</div>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center', padding: 16 }}>
                  <div style={{ fontSize: 24, fontWeight: 'bold', color: '#722ed1' }}>
                    {clickStats.unique_ips || 0}
                  </div>
                  <div style={{ color: '#999', marginTop: 8 }}>独立IP</div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card 
            title="赞助信息"
            extra={
              !sponsorship && (
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  onClick={() => setSponsorModalVisible(true)}
                >
                  申请赞助
                </Button>
              )
            }
          >
            {sponsorship ? (
              <div>
                <p><strong>赞助类型：</strong>
                  <Tag color={sponsorship.sponsorship_type === 'bidding' ? 'orange' : 'blue'}>
                    {sponsorship.sponsorship_type === 'bidding' ? '竞价排名' : 'CPC点击'}
                  </Tag>
                </p>
                <p><strong>竞价金额：</strong>¥{sponsorship.bid_amount?.toFixed(2) || '0.00'}</p>
                <p><strong>CPC单价：</strong>¥{sponsorship.cpc_price?.toFixed(2) || '0.00'}</p>
                <p><strong>每日预算：</strong>¥{sponsorship.daily_budget?.toFixed(2) || '0.00'}</p>
                <p><strong>总花费：</strong>¥{sponsorship.total_spent?.toFixed(2) || '0.00'}</p>
                <p><strong>状态：</strong>
                  <Tag color={sponsorship.status === 'active' ? 'green' : 'default'}>
                    {sponsorship.status === 'active' ? '进行中' : sponsorship.status}
                  </Tag>
                </p>
              </div>
            ) : (
              <Empty description="暂无赞助信息" size="small" />
            )}
          </Card>
        </Col>
      </Row>

      {/* 每日访问趋势 */}
      {clickStats.daily_stats && clickStats.daily_stats.length > 0 && (
        <Card title="访问趋势（最近30天）" style={{ marginBottom: 24 }}>
          <Table
            dataSource={clickStats.daily_stats}
            columns={[
              { title: '日期', dataIndex: 'date', key: 'date' },
              { title: '访问量', dataIndex: 'clicks', key: 'clicks' },
              { title: '访客数', dataIndex: 'visitors', key: 'visitors' }
            ]}
            pagination={false}
            size="small"
          />
        </Card>
      )}

      {/* 申请赞助弹窗 */}
      <Modal
        title="申请商家赞助"
        open={sponsorModalVisible}
        onCancel={() => {
          setSponsorModalVisible(false)
          sponsorForm.resetFields()
        }}
        onOk={() => sponsorForm.submit()}
        width={500}
      >
        <Form
          form={sponsorForm}
          layout="vertical"
          onFinish={handleCreateSponsorship}
          initialValues={{
            sponsorship_type: 'bidding',
            bid_amount: 100,
            daily_budget: 50
          }}
        >
          <Form.Item
            label="赞助类型"
            name="sponsorship_type"
            rules={[{ required: true, message: '请选择赞助类型' }]}
          >
            <Input disabled value="bidding" />
          </Form.Item>
          <Form.Item
            label="竞价金额（第一周，最低100元）"
            name="bid_amount"
            rules={[
              { required: true, message: '请输入竞价金额' },
              { type: 'number', min: 100, message: '竞价金额不能低于100元' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              prefix="¥"
              min={100}
              step={10}
            />
          </Form.Item>
          <Form.Item
            label="每日预算上限（最低50元）"
            name="daily_budget"
            rules={[
              { required: true, message: '请输入每日预算' },
              { type: 'number', min: 50, message: '每日预算不能低于50元' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              prefix="¥"
              min={50}
              step={10}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default MerchantDashboardPage

