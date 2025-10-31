import React, { useEffect, useState } from 'react'
import { Table, Button, Space, Tag, Input, Select, DatePicker, Upload, message, Modal, Descriptions } from 'antd'
import { PlusOutlined, UploadOutlined, SearchOutlined, EyeOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker

function Bills() {
  const [loading, setLoading] = useState(false)
  const [bills, setBills] = useState([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [filters, setFilters] = useState({})
  const [searchMerchant, setSearchMerchant] = useState('')
  const [searchCategory, setSearchCategory] = useState('')
  const [dateRange, setDateRange] = useState(null)
  const [viewModalVisible, setViewModalVisible] = useState(false)
  const [selectedBill, setSelectedBill] = useState(null)

  useEffect(() => {
    loadBills()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.current, pagination.pageSize])

  const loadBills = async () => {
    setLoading(true)
    try {
      const params = {
        limit: pagination.pageSize,
        offset: (pagination.current - 1) * pagination.pageSize,
        user_id: 1,
      }
      
      // 添加筛选参数
      if (searchMerchant) params.merchant = searchMerchant
      if (searchCategory) params.category = searchCategory
      if (dateRange && dateRange.length === 2) {
        params.start_date = dateRange[0].format('YYYY-MM-DD')
        params.end_date = dateRange[1].format('YYYY-MM-DD')
      }
      
      const res = await api.get('/bills', { params })
      // API 返回格式: { success: true, data: [...], total: ... }
      const billsData = res.success ? (res.data || []) : []
      setBills(billsData)
      setPagination({ ...pagination, total: res.total || billsData.length })
    } catch (error) {
      console.error('加载账单失败:', error)
      message.error('加载账单失败')
    } finally {
      setLoading(false)
    }
  }
  
  const handleSearch = () => {
    const newPagination = { ...pagination, current: 1 }
    setPagination(newPagination)
    setTimeout(() => {
      loadBills()
    }, 100)
  }
  
  const handleAddBill = () => {
    // 显示添加账单表单（简化版）
    Modal.info({
      title: '添加账单',
      content: (
        <div>
          <p>请使用以下方式添加账单：</p>
          <ul>
            <li>使用"上传发票"功能自动识别并添加</li>
            <li>通过API直接创建账单记录</li>
          </ul>
          <p style={{ color: '#999', fontSize: 12, marginTop: 8 }}>
            注意：创建大额账单（≥¥1000）或频繁消费时会自动触发安全预警
          </p>
        </div>
      ),
      okText: '知道了',
      width: 500
    })
  }
  
  // 处理账单创建后的预警
  const handleBillCreateAlert = (response) => {
    if (response.has_alerts) {
      const allAlerts = [...(response.alerts || []), ...(response.warnings || [])]
      
      allAlerts.forEach((alert) => {
        Modal.warning({
          title: alert.title,
          width: 600,
          content: (
            <div>
              <Alert
                message={alert.message}
                type="warning"
                showIcon
                icon={<WarningOutlined />}
                style={{ marginBottom: 16 }}
              />
              <div>
                <strong>建议：</strong>
                <ul style={{ marginTop: 8 }}>
                  {alert.suggestions?.map((suggestion, idx) => (
                    <li key={idx}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            </div>
          ),
          okText: '我知道了'
        })
      })
    }
  }
  
  const handleViewBill = async (billId) => {
    try {
      const res = await api.get(`/bills/${billId}`)
      if (res.success && res.data) {
        setSelectedBill(res.data)
        setViewModalVisible(true)
      } else {
        message.error('获取账单详情失败')
      }
    } catch (error) {
      console.error('获取账单详情失败:', error)
      message.error('获取账单详情失败')
    }
  }
  
  const handleDeleteBill = async (billId) => {
    try {
      await api.delete(`/bills/${billId}`)
      message.success('删除成功')
      loadBills()
    } catch (error) {
      console.error('删除账单失败:', error)
      message.error('删除失败')
    }
  }

  const columns = [
    {
      title: '时间',
      dataIndex: 'consume_time',
      key: 'consume_time',
      render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '商家',
      dataIndex: 'merchant',
      key: 'merchant',
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => `¥${parseFloat(amount).toFixed(2)}`,
      sorter: true,
    },
    {
      title: '类别',
      dataIndex: 'category',
      key: 'category',
      render: (category) => <Tag color="blue">{category}</Tag>,
    },
    {
      title: '支付方式',
      dataIndex: 'payment_method',
      key: 'payment_method',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => handleViewBill(record.id)}
          >
            查看
          </Button>
          <Button 
            type="link" 
            size="small" 
            danger
            icon={<DeleteOutlined />}
            onClick={() => {
              Modal.confirm({
                title: '确认删除',
                content: '确定要删除这条账单记录吗？',
                onOk: () => handleDeleteBill(record.id),
              })
            }}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>账单管理</h1>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAddBill}>
            添加账单
          </Button>
          <Upload
            action="/api/v1/invoices/upload"
            onChange={(info) => {
              if (info.file.status === 'done') {
                message.success('上传成功')
                loadBills()
              } else if (info.file.status === 'error') {
                message.error('上传失败，请检查网络连接')
              }
            }}
          >
            <Button icon={<UploadOutlined />}>上传发票</Button>
          </Upload>
        </Space>
      </div>

      <div style={{ marginBottom: 16, padding: 16, background: '#f5f7fa', borderRadius: 8 }}>
        <Space>
          <Input
            placeholder="搜索商家"
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
            allowClear
            value={searchMerchant}
            onChange={(e) => setSearchMerchant(e.target.value)}
            onPressEnter={handleSearch}
          />
          <Select
            placeholder="选择类别"
            style={{ width: 120 }}
            allowClear
            value={searchCategory}
            onChange={setSearchCategory}
          >
            <Select.Option value="餐饮">餐饮</Select.Option>
            <Select.Option value="交通">交通</Select.Option>
            <Select.Option value="购物">购物</Select.Option>
            <Select.Option value="娱乐">娱乐</Select.Option>
            <Select.Option value="医疗">医疗</Select.Option>
            <Select.Option value="教育">教育</Select.Option>
            <Select.Option value="其他">其他</Select.Option>
          </Select>
          <RangePicker 
            value={dateRange}
            onChange={setDateRange}
          />
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
            搜索
          </Button>
          <Button onClick={() => {
            setSearchMerchant('')
            setSearchCategory('')
            setDateRange(null)
            setPagination({ ...pagination, current: 1 })
            loadBills()
          }}>
            重置
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={bills}
        loading={loading}
        rowKey="id"
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
        onChange={(newPagination) => {
          setPagination(newPagination)
          setTimeout(() => loadBills(), 0)
        }}
      />

      <Modal
        title="账单详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {selectedBill && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="账单ID">{selectedBill.id}</Descriptions.Item>
            <Descriptions.Item label="消费时间">
              {dayjs(selectedBill.consume_time).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="商家">{selectedBill.merchant}</Descriptions.Item>
            <Descriptions.Item label="金额">
              <span style={{ fontSize: 18, color: '#E02020', fontWeight: 'bold' }}>
                ¥{parseFloat(selectedBill.amount).toFixed(2)}
              </span>
            </Descriptions.Item>
            <Descriptions.Item label="类别">
              <Tag color="blue">{selectedBill.category}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="支付方式">{selectedBill.payment_method}</Descriptions.Item>
            {selectedBill.location && (
              <Descriptions.Item label="位置" span={2}>{selectedBill.location}</Descriptions.Item>
            )}
            {selectedBill.description && (
              <Descriptions.Item label="备注" span={2}>{selectedBill.description}</Descriptions.Item>
            )}
            <Descriptions.Item label="创建时间">
              {selectedBill.created_at ? dayjs(selectedBill.created_at).format('YYYY-MM-DD HH:mm:ss') : '—'}
            </Descriptions.Item>
            <Descriptions.Item label="更新时间">
              {selectedBill.updated_at ? dayjs(selectedBill.updated_at).format('YYYY-MM-DD HH:mm:ss') : '—'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

export default Bills

