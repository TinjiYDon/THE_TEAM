import React, { useEffect, useState } from 'react'
import { Table, Tag, Space, Button, message } from 'antd'
import api from '../utils/api'

const levelColor = {
  high: 'red',
  medium: 'orange',
  low: 'blue'
}

function WarningCenter() {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState([])

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await api.get('/alerts?limit=100')
      setData((res && res.data) || [])
    } catch (e) {
      message.error(e?.detail || e?.message || '获取预警失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const updateStatus = async (record, status) => {
    try {
      await api.post(`/alerts/${record.id}/status`, { status })
      message.success('更新成功')
      fetchData()
    } catch (e) {
      message.error(e?.detail || e?.message || '更新失败')
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 80 },
    { title: '级别', dataIndex: 'level', width: 100, render: (v) => <Tag color={levelColor[v] || 'default'}>{v}</Tag> },
    { title: '类型', dataIndex: 'event_type', width: 160 },
    { title: '标题', dataIndex: 'title', ellipsis: true },
    { title: '原因', dataIndex: 'reason', ellipsis: true },
    { title: '状态', dataIndex: 'status', width: 120, render: (v) => <Tag>{v}</Tag> },
    { title: '时间', dataIndex: 'created_at', width: 180 },
    {
      title: '操作',
      key: 'action',
      width: 220,
      render: (_, record) => (
        <Space>
          <Button size="small" onClick={() => updateStatus(record, 'read')}>标记已读</Button>
          <Button size="small" danger onClick={() => updateStatus(record, 'ignored')}>忽略</Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>预警中心</h2>
        <Space>
          <Button onClick={fetchData}>刷新</Button>
        </Space>
      </div>
      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={data}
        pagination={{ pageSize: 10 }}
      />
    </div>
  )
}

export default WarningCenter


