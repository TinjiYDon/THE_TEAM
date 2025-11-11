import React, { useEffect, useState, useCallback } from 'react'
import { Card, Form, Input, Select, Switch, Button, Space, Typography, Divider, message, Alert, Modal, Spin, Tag } from 'antd'
import { DownloadOutlined, SafetyCertificateOutlined, SaveOutlined, ShopOutlined, SettingOutlined } from '@ant-design/icons'
import api from '../utils/api'
import { useNavigate } from 'react-router-dom'

const { Title, Paragraph, Text } = Typography

const BUDGET_CYCLE_OPTIONS = [
  { label: '按月', value: 'monthly' },
  { label: '按周', value: 'weekly' },
  { label: '按年', value: 'yearly' }
]

function ProfilePage() {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [profile, setProfile] = useState(null)
  const [exportInfo, setExportInfo] = useState(null)
  const [deactivateInfo, setDeactivateInfo] = useState(null)
  const [merchantInfo, setMerchantInfo] = useState(null)
  const [merchantVerificationVisible, setMerchantVerificationVisible] = useState(false)
  const [verificationForm] = Form.useForm()

  const loadSettings = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/account/settings')
      if (res.success) {
        const { profile: p, preferences } = res.data || {}
        setProfile(p || {})
        form.setFieldsValue({
          city: preferences?.city || '',
          job: preferences?.job || '',
          budget_cycle: preferences?.budget_cycle || 'monthly',
          notify_budget: preferences?.notify_budget ?? true,
          notify_insight: preferences?.notify_insight ?? true,
          notify_community: preferences?.notify_community ?? true
        })
      }
      
      // 加载商家信息
      const merchantRes = await api.get('/merchants/my')
      if (merchantRes.success && merchantRes.data) {
        setMerchantInfo(merchantRes.data)
      }
    } catch (error) {
      message.error(error.detail || '获取个人设置失败')
    } finally {
      setLoading(false)
    }
  }, [form])

  useEffect(() => {
    loadSettings()
  }, [loadSettings])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      const res = await api.put('/account/settings', values)
      if (res.success) {
        message.success('设置已保存')
        loadSettings()
      } else {
        message.error(res.detail || '保存失败')
      }
    } catch (error) {
      if (!error?.errorFields) {
        message.error(error.detail || '保存失败')
      }
    } finally {
      setSaving(false)
    }
  }

  const handleExport = async () => {
    try {
      const res = await api.post('/account/export', { note: '用户中心申请导出数据包' })
      if (res.success) {
        setExportInfo(res.data)
        message.success('导出申请已提交，请等待后台处理')
      } else {
        message.error(res.detail || '导出申请失败')
      }
    } catch (error) {
      message.error(error.detail || '导出申请失败')
    }
  }

  const handleDeactivate = () => {
    Modal.confirm({
      title: '确认提交注销申请？',
      content: '提交后管理员会审核注销请求，审核通过后账户将被停用。',
      okText: '提交申请',
      cancelText: '取消',
      onOk: async () => {
        try {
          const res = await api.post('/account/deactivate', { note: '用户中心发起注销申请' })
          if (res.success) {
            setDeactivateInfo(res.data)
            message.success('注销申请已提交')
          } else {
            message.error(res.detail || '注销申请失败')
          }
        } catch (error) {
          message.error(error.detail || '注销申请失败')
        }
      }
    })
  }

  const handleMerchantVerification = async (values) => {
    try {
      const res = await api.post('/merchants/verify', values)
      if (res.success) {
        message.success('商家认证申请已提交，等待审核')
        setMerchantVerificationVisible(false)
        verificationForm.resetFields()
        loadSettings()
      } else {
        message.error(res.detail || '认证申请失败')
      }
    } catch (error) {
      message.error(error.detail || '认证申请失败')
    }
  }

  const getMerchantStatusTag = (status) => {
    const statusMap = {
      'pending': { color: 'orange', text: '审核中' },
      'approved': { color: 'green', text: '已认证' },
      'rejected': { color: 'red', text: '已拒绝' }
    }
    const statusInfo = statusMap[status] || { color: 'default', text: status }
    return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
  }

  return (
    <Spin spinning={loading} tip="加载中…">
      <Space direction="vertical" style={{ width: '100%', padding: 24 }} size="large">
        <Title level={3}>个人中心</Title>

        <Card title="基础资料">
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Text type="secondary">当前账号</Text>
              <Paragraph strong style={{ marginBottom: 0 }}>{profile?.username || 'demo_user'}</Paragraph>
              <Text type="secondary">{profile?.email || '未绑定邮箱'}</Text>
              {profile?.phone ? <Paragraph style={{ marginTop: 8 }}>联系电话：{profile.phone}</Paragraph> : null}
            </div>
            <Alert
              type="info"
              showIcon
              message="提示"
              description="资料更新会影响 AI 画像与推荐结果，建议每季度回顾一次。"
            />
          </Space>
        </Card>

        <Card title="资料与偏好设置">
          <Form
            form={form}
            layout="vertical"
            initialValues={{
              city: '',
              job: '',
              budget_cycle: 'monthly',
              notify_budget: true,
              notify_insight: true,
              notify_community: true
            }}
          >
            <Form.Item label="所在城市" name="city">
              <Input placeholder="例如：上海市" />
            </Form.Item>
            <Form.Item label="职业" name="job">
              <Input placeholder="例如：产品经理" />
            </Form.Item>
            <Form.Item label="预算周期" name="budget_cycle">
              <Select options={BUDGET_CYCLE_OPTIONS} />
            </Form.Item>
            <Divider />
            <Form.Item label="预算提醒" name="notify_budget" valuePropName="checked">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Form.Item label="AI 洞察通知" name="notify_insight" valuePropName="checked">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Form.Item label="社群消息推送" name="notify_community" valuePropName="checked">
              <Switch checkedChildren="开启" unCheckedChildren="关闭" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} loading={saving}>
                保存设置
              </Button>
            </Form.Item>
          </Form>
        </Card>

        {/* 商家认证和管理 */}
        <Card 
          title={
            <span>
              <ShopOutlined style={{ marginRight: 8 }} />
              商家认证与管理
            </span>
          }
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {merchantInfo ? (
              <>
                <Alert
                  type="info"
                  showIcon
                  message="商家认证状态"
                  description={
                    <div>
                      <p><strong>商家名称：</strong>{merchantInfo.merchant_name}</p>
                      <p><strong>类别：</strong>{merchantInfo.category}</p>
                      <p><strong>状态：</strong>{getMerchantStatusTag(merchantInfo.status)}</p>
                      {merchantInfo.status === 'approved' && (
                        <Button
                          type="primary"
                          icon={<SettingOutlined />}
                          onClick={() => navigate('/merchants/dashboard')}
                          style={{ marginTop: 8 }}
                        >
                          进入商家后台
                        </Button>
                      )}
                    </div>
                  }
                />
              </>
            ) : (
              <>
                <Alert
                  type="info"
                  showIcon
                  message="商家认证"
                  description="认证商家后，您可以管理店铺信息、查看点击量和转化率、申请赞助等。"
                />
                <Button
                  type="primary"
                  icon={<ShopOutlined />}
                  onClick={() => setMerchantVerificationVisible(true)}
                >
                  申请商家认证
                </Button>
              </>
            )}
          </Space>
        </Card>

        <Card title="数据导出与安全">
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Alert
              type="info"
              showIcon
              message="数据导出"
              description="申请后将生成 CSV/JSON 数据包，需管理员审核通过后可下载。"
            />
            {exportInfo ? (
              <Alert
                type="success"
                showIcon
                message="导出申请已提交"
                description={`请求编号：${exportInfo.request_id}，状态：${exportInfo.status}`}
              />
            ) : null}
            <Button icon={<DownloadOutlined />} onClick={handleExport}>
              提交导出申请
            </Button>
            <Divider />
            {deactivateInfo ? (
              <Alert
                type="warning"
                showIcon
                message="注销申请已提交"
                description={`请求编号：${deactivateInfo.request_id}，状态：${deactivateInfo.status}`}
              />
            ) : (
              <Alert
                type="warning"
                showIcon
                message="注销说明"
                description="提交注销后，管理员会进行人工确认；审批完成前可随时联系管理员撤销。"
              />
            )}
            <Button danger icon={<SafetyCertificateOutlined />} onClick={handleDeactivate}>
              提交注销申请
            </Button>
          </Space>
        </Card>

        {/* 商家认证弹窗 */}
        <Modal
          title="商家认证申请"
          open={merchantVerificationVisible}
          onCancel={() => {
            setMerchantVerificationVisible(false)
            verificationForm.resetFields()
          }}
          onOk={() => verificationForm.submit()}
          width={600}
        >
          <Form
            form={verificationForm}
            layout="vertical"
            onFinish={handleMerchantVerification}
          >
            <Form.Item
              label="商家名称"
              name="merchant_name"
              rules={[{ required: true, message: '请输入商家名称' }]}
            >
              <Input placeholder="请输入商家名称" />
            </Form.Item>
            <Form.Item
              label="经营许可证号"
              name="business_license"
              rules={[{ required: true, message: '请输入经营许可证号' }]}
            >
              <Input placeholder="请输入经营许可证号" />
            </Form.Item>
            <Form.Item
              label="商家类别"
              name="category"
              rules={[{ required: true, message: '请选择商家类别' }]}
            >
              <Select placeholder="请选择商家类别">
                <Select.Option value="餐饮">餐饮</Select.Option>
                <Select.Option value="交通">交通</Select.Option>
                <Select.Option value="购物">购物</Select.Option>
                <Select.Option value="娱乐">娱乐</Select.Option>
                <Select.Option value="医疗">医疗</Select.Option>
                <Select.Option value="教育">教育</Select.Option>
                <Select.Option value="其他">其他</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item
              label="许可证图片（可选）"
              name="license_image_path"
            >
              <Input placeholder="许可证图片路径（上传功能待实现）" />
            </Form.Item>
            <Alert
              type="warning"
              message="认证说明"
              description="请确保提供的信息真实有效。认证申请提交后，管理员会在48小时内审核。"
              showIcon
              style={{ marginTop: 16 }}
            />
          </Form>
        </Modal>
      </Space>
    </Spin>
  )
}

export default ProfilePage

