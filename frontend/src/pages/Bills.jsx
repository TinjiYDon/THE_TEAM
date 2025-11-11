import React, { useEffect, useState, useRef } from 'react'
import { Table, Button, Space, Tag, Input, Select, DatePicker, Upload, message, Modal, Descriptions, Alert, Dropdown, Checkbox, Card, Grid } from 'antd'
import { PlusOutlined, UploadOutlined, SearchOutlined, EyeOutlined, DeleteOutlined, FileExcelOutlined, PictureOutlined } from '@ant-design/icons'
import api from '../utils/api'
import { gradientBg } from '../theme'
import dayjs from 'dayjs'
// 暂时移除react-window虚拟滚动，使用普通渲染
// import { FixedSizeList } from 'react-window'
import { getCurrentUserId } from '../utils/session'

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
  const [error, setError] = useState(null)
  const [visibleColumns, setVisibleColumns] = useState(['consume_time','merchant','amount','category','payment_method','action'])
  const debounceTimerRef = useRef(null)
  const [enableInfinite, setEnableInfinite] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [cardView, setCardView] = useState(false)
  const screens = Grid.useBreakpoint()

  useEffect(() => {
    loadBills()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.current, pagination.pageSize])

  // 根据屏幕自动切换默认视图（小屏优先卡片）
  useEffect(() => {
    if (screens && typeof screens.md !== 'undefined') {
      setCardView(!screens.md)
    }
  }, [screens])

  const loadBills = async (append = false) => {
    append ? setLoadingMore(true) : setLoading(true)
    try {
      setError(null)
      const params = {
        limit: pagination.pageSize,
        offset: (pagination.current - 1) * pagination.pageSize,
        user_id: getCurrentUserId(),
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
      setBills(append ? [...bills, ...billsData] : billsData)
      setPagination({ ...pagination, total: res.total || (append ? bills.length + billsData.length : billsData.length) })
    } catch (error) {
      console.error('加载账单失败:', error)
      setError(error)
      message.error('加载账单失败')
    } finally {
      append ? setLoadingMore(false) : setLoading(false)
    }
  }
  
  const handleSearch = () => {
    const newPagination = { ...pagination, current: 1 }
    setPagination(newPagination)
    setTimeout(() => {
      loadBills()
    }, 100)
  }
  
  // 输入防抖：商家搜索
  useEffect(() => {
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current)
    debounceTimerRef.current = setTimeout(() => {
      const newPagination = { ...pagination, current: 1 }
      setPagination(newPagination)
      loadBills()
    }, 300)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchMerchant])

  // 无限滚动（流式加载）
  useEffect(() => {
    if (!enableInfinite) return
    const el = document.querySelector('.bills-table .ant-table-body')
    if (!el) return
    const onScroll = () => {
      const nearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 40
      const hasMore = bills.length < pagination.total
      if (nearBottom && hasMore && !loadingMore && !loading) {
        const nextPage = pagination.current + 1
        setPagination(prev => ({ ...prev, current: nextPage }))
        setTimeout(() => loadBills(true), 0)
      }
    }
    el.addEventListener('scroll', onScroll)
    return () => el.removeEventListener('scroll', onScroll)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enableInfinite, bills, pagination.current, pagination.total, loadingMore, loading])

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

  const exportCSV = () => {
    if (!bills || bills.length === 0) {
      message.info('暂无可导出的数据')
      return
    }
    const headers = ['ID','时间','商家','金额','类别','支付方式']
    const rows = bills.map(b => [
      b.id,
      dayjs(b.consume_time).format('YYYY-MM-DD HH:mm:ss'),
      (b.merchant || '').replace(/\"/g,'\\"'),
      parseFloat(b.amount).toFixed(2),
      b.category || '',
      b.payment_method || ''
    ])
    const csv = [headers, ...rows].map(r => r.map(x => `"${x}"`).join(',')).join('\n')
    const blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `bills_${dayjs().format('YYYYMMDD_HHmmss')}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const extractFilename = (disposition, fallback) => {
    if (!disposition) return fallback
    const match = disposition.match(/filename\*=UTF-8''(.+)|filename=\"(.+)\"/)
    const encoded = match?.[1]
    const quoted = match?.[2]
    try {
      if (encoded) return decodeURIComponent(encoded)
      if (quoted) return quoted
    } catch {}
    return fallback
  }

  const exportExcel = async () => {
    try {
      const hide = message.loading('正在导出 Excel...', 0)
      const res = await fetch(`/api/v1/bills/export/excel?user_id=${getCurrentUserId()}`)
      hide()
      if (!res.ok) {
        throw new Error('导出失败')
      }
      const blob = await res.blob()
      const disposition = res.headers.get('content-disposition')
      const filename = extractFilename(disposition, `bills_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
      message.success('Excel 导出成功')
    } catch (error) {
      console.error('导出 Excel 失败:', error)
      message.error('导出 Excel 失败，请稍后再试')
    }
  }

  const exportLongImage = async (view = 'list', trendPeriod = 'month') => {
    try {
      const params = new URLSearchParams({ user_id: getCurrentUserId(), view })
      if (view === 'trend') {
        params.set('period', trendPeriod)
      }
      const hide = message.loading('正在生成长图...', 0)
      const res = await fetch(`/api/v1/bills/export/image?${params.toString()}`)
      hide()
      if (!res.ok) {
        throw new Error('导出失败')
      }
      const blob = await res.blob()
      const disposition = res.headers.get('content-disposition')
      const fallbackName = view === 'trend'
        ? `bills_trend_${trendPeriod}_${dayjs().format('YYYYMMDD_HHmmss')}.png`
        : `bills_list_${dayjs().format('YYYYMMDD_HHmmss')}.png`
      const filename = extractFilename(disposition, fallbackName)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
      message.success('长图导出成功')
    } catch (error) {
      console.error('导出长图失败:', error)
      message.error('导出长图失败，请稍后再试')
    }
  }

  const longImageMenu = {
    items: [
      { key: 'list', label: '账单列表长图' },
      { key: 'trend:day', label: '趋势长图（日）' },
      { key: 'trend:week', label: '趋势长图（周）' },
      { key: 'trend:month', label: '趋势长图（月）' },
      { key: 'trend:year', label: '趋势长图（年）' },
    ],
    onClick: ({ key }) => {
      if (key === 'list') {
        exportLongImage('list')
      } else {
        const [, period = 'month'] = key.split(':')
        exportLongImage('trend', period)
      }
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

  const allColumns = [
    {
      title: '时间',
      dataIndex: 'consume_time',
      key: 'consume_time',
      render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm'),
      responsive: ['xs','sm','md','lg','xl'],
    },
    {
      title: '商家',
      dataIndex: 'merchant',
      key: 'merchant',
      responsive: ['xs','sm','md','lg','xl'],
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => `¥${parseFloat(amount).toFixed(2)}`,
      sorter: true,
      responsive: ['xs','sm','md','lg','xl'],
    },
    {
      title: '类别',
      dataIndex: 'category',
      key: 'category',
      render: (category) => <Tag color="blue">{category}</Tag>,
      responsive: ['sm','md','lg','xl'],
    },
    {
      title: '支付方式',
      dataIndex: 'payment_method',
      key: 'payment_method',
      responsive: ['md','lg','xl'],
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

  // 列显隐：从本地存储恢复/持久化
  const COLS_KEY = 'bills_visible_cols_v1'
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(COLS_KEY) || 'null')
      if (Array.isArray(saved) && saved.length > 0) setVisibleColumns(saved)
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  useEffect(() => {
    localStorage.setItem(COLS_KEY, JSON.stringify(visibleColumns))
  }, [visibleColumns])

  const columns = allColumns.filter(col => visibleColumns.includes(col.key))

  const columnMenuItems = allColumns.map(col => ({
    key: col.key,
    label: (
      <Checkbox
        checked={visibleColumns.includes(col.key)}
        onChange={(e) => {
          const checked = e.target.checked
          setVisibleColumns(prev => {
            const base = new Set(prev)
            if (checked) base.add(col.key); else base.delete(col.key)
            // 至少保留一列
            const next = Array.from(base)
            return next.length === 0 ? prev : next
          })
        }}
      >
        {col.title}
      </Checkbox>
    )
  }))

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>账单管理</h1>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAddBill}>
            添加账单
          </Button>
          <Button onClick={exportCSV}>导出 CSV</Button>
          <Button icon={<FileExcelOutlined />} onClick={exportExcel}>
            导出 Excel
          </Button>
          <Dropdown menu={longImageMenu} trigger={['click']}>
            <Button icon={<PictureOutlined />}>导出长图</Button>
          </Dropdown>
          <Dropdown
            menu={{
              items: columnMenuItems
            }}
            trigger={['click']}
          >
            <Button>列显示设置</Button>
          </Dropdown>
          <Button onClick={() => setCardView(v => !v)}>
            {cardView ? '切换为表格' : '切换为卡片'}
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

      <div style={{ marginBottom: 16, padding: 16, borderRadius: 12, ...gradientBg }}>
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
        {error && (
          <div style={{ marginTop: 12 }}>
            <Alert type="warning" showIcon message="加载失败" description="请检查网络或后端服务" />
          </div>
        )}
      </div>

      {cardView ? (
        <div style={{ maxHeight: 600, overflowY: 'auto' }}>
          {bills.map(b => (
            <div style={{ padding: '0 0 12px 0' }} key={b.id}>
              <Card>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong>{b.merchant}</strong>
                    <span style={{ color: '#E02020', fontWeight: 600 }}>¥{parseFloat(b.amount).toFixed(2)}</span>
                  </div>
                  <div style={{ color: '#999' }}>{dayjs(b.consume_time).format('YYYY-MM-DD HH:mm')}</div>
                  <div>
                    <Tag color="blue" style={{ marginRight: 8 }}>{b.category}</Tag>
                    <span>{b.payment_method}</span>
                  </div>
                  <Space>
                    <Button size="small" onClick={() => handleViewBill(b.id)} icon={<EyeOutlined />}>查看</Button>
                    <Button size="small" danger onClick={() => {
                      Modal.confirm({
                        title: '确认删除',
                        content: '确定要删除这条账单记录吗？',
                        onOk: () => handleDeleteBill(b.id),
                      })
                    }} icon={<DeleteOutlined />}>删除</Button>
                  </Space>
                </Space>
              </Card>
            </div>
          ))}
        </div>
      ) : (
        <Table
          className="bills-table"
          columns={columns}
          dataSource={bills}
          loading={loading}
          rowKey="id"
          size="middle"
          sticky
          scroll={{ y: 520, x: 'max-content' }}
          locale={{
            emptyText: '暂无账单数据，试试调整筛选条件或添加账单',
          }}
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
      )}

      {loadingMore && (
        <div style={{ textAlign: 'center', color: '#999', padding: 8 }}>加载更多...</div>
      )}

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

