import React, { useEffect, useState } from 'react'
import { Form, InputNumber, Switch, TimePicker, Button, Card, Space, message } from 'antd'
import dayjs from 'dayjs'
import api from '../utils/api'

function WarningSettings() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.get('/settings/alert_prefs')
      const d = res?.data
      if (d) {
        form.setFieldsValue({
          threshold_high: d.threshold_high,
          threshold_medium: d.threshold_medium,
          channel_email: !!d.channel_email,
          channel_sms: !!d.channel_sms,
          channel_wecom: !!d.channel_wecom,
          channel_wechat_mp: !!d.channel_wechat_mp,
          quiet_hours: [
            dayjs(d.quiet_hours_start || '22:00', 'HH:mm'),
            dayjs(d.quiet_hours_end || '07:00', 'HH:mm')
          ],
          break_quiet_for_high: !!d.break_quiet_for_high,
          rate_limit_per_hour: d.rate_limit_per_hour || 5
        })
      }
    } catch (e) {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const onFinish = async (values) => {
    try {
      const payload = {
        threshold_high: values.threshold_high,
        threshold_medium: values.threshold_medium,
        channel_email: values.channel_email,
        channel_sms: values.channel_sms,
        channel_wecom: values.channel_wecom,
        channel_wechat_mp: values.channel_wechat_mp,
        quiet_hours_start: values.quiet_hours?.[0]?.format('HH:mm') || '22:00',
        quiet_hours_end: values.quiet_hours?.[1]?.format('HH:mm') || '07:00',
        break_quiet_for_high: values.break_quiet_for_high,
        rate_limit_per_hour: values.rate_limit_per_hour
      }
      await api.post('/settings/alert_prefs', payload)
      message.success('已保存')
    } catch (e) {
      message.error(e?.detail || e?.message || '保存失败')
    }
  }

  return (
    <Card title="预警设置" loading={loading}>
      <Form form={form} layout="vertical" onFinish={onFinish} initialValues={{
        threshold_high: 0.8,
        threshold_medium: 0.5,
        channel_email: true,
        channel_wecom: true,
        rate_limit_per_hour: 5,
        break_quiet_for_high: true
      }}>
        <Space size="large" style={{ display: 'flex', flexWrap: 'wrap' }}>
          <Form.Item label="高风险阈值" name="threshold_high">
            <InputNumber min={0} max={1} step={0.05} />
          </Form.Item>
          <Form.Item label="中风险阈值" name="threshold_medium">
            <InputNumber min={0} max={1} step={0.05} />
          </Form.Item>
          <Form.Item label="每小时通知上限" name="rate_limit_per_hour">
            <InputNumber min={1} max={60} />
          </Form.Item>
        </Space>
        <Space size="large" style={{ display: 'flex', flexWrap: 'wrap' }}>
          <Form.Item label="邮件通知" name="channel_email" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="短信通知" name="channel_sms" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="企业微信" name="channel_wecom" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="公众号模板消息" name="channel_wechat_mp" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Space>
        <Space size="large" style={{ display: 'flex', flexWrap: 'wrap' }}>
          <Form.Item label="静默时段" name="quiet_hours">
            <TimePicker.RangePicker format="HH:mm" minuteStep={5} />
          </Form.Item>
          <Form.Item label="高风险突破静默" name="break_quiet_for_high" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Space>
        <Form.Item>
          <Button type="primary" htmlType="submit">保存</Button>
        </Form.Item>
      </Form>
    </Card>
  )
}

export default WarningSettings


