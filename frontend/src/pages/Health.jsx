import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Form, Input, Button, Alert, Progress, Statistic, message, Modal } from 'antd'
import { DollarOutlined, WarningOutlined, CheckCircleOutlined } from '@ant-design/icons'
import api from '../utils/api'

function Health() {
  const [form] = Form.useForm()
  const [budgets, setBudgets] = useState([])
  const [loading, setLoading] = useState(false)
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    loadBudgets()
    loadAlerts()
  }, [])

  const loadBudgets = async () => {
    try {
      const res = await api.get('/budgets?user_id=1')
      if (res.success && res.data) {
        setBudgets(res.data || [])
      }
    } catch (error) {
      console.error('加载预算失败:', error)
    }
  }

  const loadAlerts = async () => {
    try {
      const res = await api.get('/budgets/alerts?user_id=1')
      if (res.success && res.data) {
        setAlerts(res.data || [])
      }
    } catch (error) {
      console.error('加载预警失败:', error)
    }
  }

  const handleCreateBudget = async (values) => {
    try {
      const res = await api.post('/budgets', {
        ...values,
        user_id: 1,
        monthly_budget: parseFloat(values.monthly_budget),
        alert_threshold: 0.8
      })
      if (res.success) {
        message.success('预算设置成功！')
        form.resetFields()
        loadBudgets()
      }
    } catch (error) {
      message.error('设置预算失败')
    }
  }

  const handleUpdateBudget = async (budgetId, values) => {
    try {
      const res = await api.put(`/budgets/${budgetId}`, values)
      if (res.success) {
        message.success('预算更新成功！')
        loadBudgets()
      }
    } catch (error) {
      message.error('更新预算失败')
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24, fontSize: 24, fontWeight: 'bold' }}>健康消费</h1>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="设置预算" style={{ marginBottom: 16 }}>
            <Form form={form} layout="vertical" onFinish={handleCreateBudget}>
              <Form.Item
                name="category"
                label="消费类别"
                rules={[{ required: true, message: '请选择类别' }]}
              >
                <Input placeholder="如：餐饮、购物、交通等" />
              </Form.Item>
              <Form.Item
                name="monthly_budget"
                label="月度预算（元）"
                rules={[
                  { required: true, message: '请输入预算金额' },
                  { type: 'number', min: 0.01, message: '预算必须大于0' }
                ]}
              >
                <Input type="number" placeholder="输入月度预算" step="0.01" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" block>
                  设置预算
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="预算概览">
            {budgets.length === 0 ? (
              <Alert
                message="暂无预算设置"
                description="请设置您的月度预算，系统将自动监控消费情况并提醒您"
                type="info"
                showIcon
              />
            ) : (
              <div>
                {budgets.map((budget) => {
                  const usage = budget.current_spent / budget.monthly_budget
                  const percent = (usage * 100).toFixed(1)
                  const isOver = usage >= 1
                  const isWarning = usage >= budget.alert_threshold

                  return (
                    <Card key={budget.id} size="small" style={{ marginBottom: 12 }}>
                      <div style={{ marginBottom: 8 }}>
                        <strong>{budget.category || '总计'}</strong>
                      </div>
                      <Progress
                        percent={parseFloat(percent)}
                        status={isOver ? 'exception' : isWarning ? 'active' : 'success'}
                        strokeColor={isOver ? '#ff4d4f' : isWarning ? '#faad14' : '#52c41a'}
                      />
                      <Row gutter={8} style={{ marginTop: 8 }}>
                        <Col span={12}>
                          <Statistic
                            title="已消费"
                            value={budget.current_spent}
                            prefix={<DollarOutlined />}
                            suffix="元"
                            valueStyle={{ fontSize: 14 }}
                          />
                        </Col>
                        <Col span={12}>
                          <Statistic
                            title="预算"
                            value={budget.monthly_budget}
                            prefix={<DollarOutlined />}
                            suffix="元"
                            valueStyle={{ fontSize: 14 }}
                          />
                        </Col>
                      </Row>
                      {isWarning && (
                        <Alert
                          message={isOver ? '已超额！' : '即将超额！'}
                          description={`已使用 ${percent}%，${isOver ? '请控制消费' : '请注意控制消费'}`}
                          type={isOver ? 'error' : 'warning'}
                          showIcon
                          style={{ marginTop: 8 }}
                        />
                      )}
                    </Card>
                  )
                })}
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {alerts.length > 0 && (
        <Card title="消费预警" style={{ marginTop: 16 }}>
          {alerts.map((alert, idx) => (
            <Alert
              key={idx}
              message={`${alert.category}预算预警`}
              description={`已使用 ${(alert.usage_ratio * 100).toFixed(1)}%，超过预警阈值 ${(alert.alert_threshold * 100).toFixed(0)}%`}
              type="warning"
              showIcon
              icon={<WarningOutlined />}
              style={{ marginBottom: 12 }}
              action={
                <Button size="small" onClick={() => Modal.info({
                  title: '消费建议',
                  content: '建议您控制该类别消费，避免超支。可以查看详细账单分析，了解具体消费情况。'
                })}>
                  查看建议
                </Button>
              }
            />
          ))}
        </Card>
      )}

      <Card title="消费提醒设置" style={{ marginTop: 16 }}>
        <Alert
          message="自动提醒功能"
          description="系统会在您消费时自动检测：1. 单笔大额消费（≥1000元）将提醒防诈骗；2. 短时间频繁消费将提醒过度消费风险；3. 接近预算限额时提前预警；4. 超出预算时立即提醒"
          type="info"
          showIcon
        />
      </Card>
    </div>
  )
}

export default Health

