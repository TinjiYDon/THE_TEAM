import React, { useState } from 'react'
import { Card, Form, Input, Select, Button, message, Alert } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import api from '../utils/api'

const { TextArea } = Input
const { Option } = Select

const FEEDBACK_TYPES = [
  { label: '功能建议', value: 'function' },
  { label: '商家信息', value: 'merchant_info' },
  { label: '店铺信息', value: 'shop_info' },
  { label: '其他建议', value: 'suggestion' }
]

function FeedbackPage() {
  const [form] = Form.useForm()
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async (values) => {
    setSubmitting(true)
    try {
      const res = await api.post('/feedback', values)
      if (res.success) {
        message.success('反馈已提交，感谢您的建议！')
        form.resetFields()
        setSubmitted(true)
        setTimeout(() => setSubmitted(false), 5000)
      } else {
        message.error(res.detail || '提交失败')
      }
    } catch (error) {
      message.error('提交反馈失败')
      console.error(error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <Card>
        <h1 style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 24 }}>意见反馈</h1>
        
        {submitted && (
          <Alert
            type="success"
            message="反馈已提交"
            description="您的反馈已成功提交，我们会认真考虑您的建议。感谢您的支持！"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            feedback_type: 'suggestion'
          }}
        >
          <Form.Item
            label="反馈类型"
            name="feedback_type"
            rules={[{ required: true, message: '请选择反馈类型' }]}
          >
            <Select placeholder="请选择反馈类型">
              {FEEDBACK_TYPES.map(type => (
                <Option key={type.value} value={type.value}>{type.label}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="标题（可选）"
            name="title"
          >
            <Input placeholder="简要描述您的反馈" />
          </Form.Item>

          <Form.Item
            label="详细内容"
            name="content"
            rules={[
              { required: true, message: '请输入反馈内容' },
              { min: 10, message: '反馈内容至少10个字符' }
            ]}
          >
            <TextArea
              rows={6}
              placeholder="请详细描述您的问题或建议..."
              showCount
              maxLength={1000}
            />
          </Form.Item>

          <Form.Item
            label="联系邮箱（可选）"
            name="contact_email"
            rules={[
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="如需回复，请留下您的邮箱" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SendOutlined />}
              loading={submitting}
              size="large"
              block
            >
              提交反馈
            </Button>
          </Form.Item>
        </Form>

        <Alert
          type="info"
          message="反馈说明"
          description="您的反馈将发送至管理员邮箱，我们会认真处理每一条反馈。对于功能建议和商家信息问题，我们会在3-5个工作日内回复。"
          showIcon
          style={{ marginTop: 24 }}
        />
      </Card>
    </div>
  )
}

export default FeedbackPage

