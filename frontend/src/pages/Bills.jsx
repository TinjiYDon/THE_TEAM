import React, { useEffect, useState } from 'react'
import { Table, Button, Space, Tag, Input, Select, DatePicker, Upload, message } from 'antd'
import { PlusOutlined, UploadOutlined, SearchOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker

function Bills() {
  const [loading, setLoading] = useState(false)
  const [bills, setBills] = useState([])
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [filters, setFilters] = useState({})

  useEffect(() => {
    loadBills()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.current, pagination.pageSize])

  const loadBills = async () => {
    setLoading(true)
    try {
      const res = await api.get('/bills', {
        params: {
          limit: pagination.pageSize,
          offset: (pagination.current - 1) * pagination.pageSize,
          ...filters
        }
      })
      setBills(res.data.data || [])
      setPagination({ ...pagination, total: res.data.total || 0 })
    } catch (error) {
      message.error('加载账单失败')
    } finally {
      setLoading(false)
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
          <Button type="link" size="small">查看</Button>
          <Button type="link" size="small" danger>删除</Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>账单管理</h1>
        <Space>
          <Button type="primary" icon={<PlusOutlined />}>添加账单</Button>
          <Upload
            action="/api/v1/invoices/upload"
            onChange={(info) => {
              if (info.file.status === 'done') {
                message.success('上传成功')
                loadBills()
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
          />
          <Select
            placeholder="选择类别"
            style={{ width: 120 }}
            allowClear
          >
            <Select.Option value="餐饮">餐饮</Select.Option>
            <Select.Option value="交通">交通</Select.Option>
            <Select.Option value="购物">购物</Select.Option>
          </Select>
          <RangePicker />
          <Button type="primary">搜索</Button>
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
        onChange={(newPagination) => setPagination(newPagination)}
      />
    </div>
  )
}

export default Bills

