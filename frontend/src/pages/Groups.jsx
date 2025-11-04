import React, { useEffect, useState, useMemo } from 'react'
import { Card, Button, Space, Input, message, Spin, Empty, Select, Tag, Image } from 'antd'
import { SearchOutlined, UserOutlined } from '@ant-design/icons'
import api from '../utils/api'
import { getCurrentUserId, getCurrentCity } from '../utils/session'
import { useNavigate, useParams } from 'react-router-dom'

function Groups() {
  const { id } = useParams()
  if (id) {
    return <GroupDetail />
  }
  const [loading, setLoading] = useState(false)
  const [groups, setGroups] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCity, setSelectedCity] = useState(getCurrentCity())
  const [selectedType, setSelectedType] = useState('')
  const userId = useMemo(() => getCurrentUserId(), [])
  const navigate = useNavigate()

  useEffect(() => {
    loadGroups()
  }, [searchQuery, selectedCity, selectedType])

  const loadGroups = async () => {
    setLoading(true)
    try {
      const params = {
        city: selectedCity || undefined,
        type: selectedType || undefined,
        q: searchQuery || undefined,
        limit: 50,
      }
      const res = await api.get('/groups', { params })
      setGroups(res.data || res || [])
    } catch (error) {
      console.error('加载群组失败:', error)
      setGroups([])
    } finally {
      setLoading(false)
    }
  }

  const handleJoin = async (groupId) => {
    try {
      await api.post(`/groups/${groupId}/join`, null, { params: { user_id: userId } })
      message.success('已加入群组')
      loadGroups()
    } catch (e) {
      message.error('加入失败')
    }
  }

  const getCityName = (code) => {
    const map = { shanghai: '上海', beijing: '北京', suzhou: '苏州', '': '全部' }
    return map[code] || code
  }

  const getTypeName = (type) => {
    const map = { catering: '餐饮', finance: '理财', education: '教育', parenting: '亲子', commute: '通勤' }
    return map[type] || type
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>群组列表</h1>
      </div>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="搜索群组"
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onPressEnter={loadGroups}
            allowClear
          />
          <Select
            style={{ width: 120 }}
            value={selectedCity}
            onChange={setSelectedCity}
            allowClear
          >
            <Select.Option value="">全部城市</Select.Option>
            <Select.Option value="shanghai">上海</Select.Option>
            <Select.Option value="beijing">北京</Select.Option>
            <Select.Option value="suzhou">苏州</Select.Option>
          </Select>
          <Select
            style={{ width: 120 }}
            value={selectedType}
            onChange={setSelectedType}
            allowClear
          >
            <Select.Option value="">全部类型</Select.Option>
            <Select.Option value="catering">餐饮</Select.Option>
            <Select.Option value="finance">理财</Select.Option>
            <Select.Option value="education">教育</Select.Option>
            <Select.Option value="parenting">亲子</Select.Option>
            <Select.Option value="commute">通勤</Select.Option>
          </Select>
          <Button onClick={loadGroups}>刷新</Button>
        </Space>
      </Card>

      {loading && groups.length === 0 ? (
        <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
      ) : groups.length === 0 ? (
        <Empty description="暂无群组" />
      ) : (
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {groups.map((group) => (
            <Card
              key={group.id}
              hoverable
              onClick={() => navigate(`/groups/${group.id}`)}
              title={
                <Space>
                  <img
                    src={group.cover_url || `/groups/${group.city}-${group.type}.jpg`}
                    alt={group.name}
                    style={{ width: 48, height: 48, borderRadius: 4, objectFit: 'cover' }}
                    onError={(e) => {
                      e.target.style.display = 'none'
                    }}
                  />
                  <span>{group.name}</span>
                  <Tag>{getCityName(group.city)}</Tag>
                  <Tag color="blue">{getTypeName(group.type)}</Tag>
                </Space>
              }
              extra={
                <Button
                  type="primary"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleJoin(group.id)
                  }}
                >
                  加入群组
                </Button>
              }
            >
              <p>{group.description || '暂无描述'}</p>
              <div style={{ color: '#999', fontSize: 12 }}>
                <Space>
                  <span>成员数: {group.members || 0}</span>
                  <span>级别: {group.level || 'city'}</span>
                </Space>
              </div>
            </Card>
          ))}
        </Space>
      )}
    </div>
  )
}

export function GroupDetail() {
  const { id } = useParams()
  const [loading, setLoading] = useState(false)
  const [group, setGroup] = useState(null)
  const [posts, setPosts] = useState([])
  const userId = useMemo(() => getCurrentUserId(), [])

  useEffect(() => {
    if (id) {
      loadGroup()
      loadPosts()
    }
  }, [id])

  const loadGroup = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/groups/${id}`, { params: { user_id: userId } })
      setGroup(res.data || res)
    } catch (error) {
      message.error('加载群组详情失败')
    } finally {
      setLoading(false)
    }
  }

  const loadPosts = async () => {
    try {
      const res = await api.get('/community/feed', {
        params: { user_id: userId, group_id: id, limit: 20 }
      })
      setPosts(res.data || res || [])
    } catch (e) {
      // ignore
    }
  }

  const handleJoin = async () => {
    try {
      await api.post(`/groups/${id}/join`, null, { params: { user_id: userId } })
      message.success('已加入群组')
      loadGroup()
    } catch (e) {
      message.error('加入失败')
    }
  }

  const handleLeave = async () => {
    try {
      await api.post(`/groups/${id}/leave`, null, { params: { user_id: userId } })
      message.success('已退出群组')
      loadGroup()
    } catch (e) {
      message.error('退出失败')
    }
  }

  if (loading) {
    return <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
  }

  if (!group) {
    return <Empty description="群组不存在" />
  }

  return (
    <div>
      <Card
        cover={
          <img
            src={group.cover_url || `/groups/${group.city}-${group.type}.jpg`}
            alt={group.name}
            style={{ width: '100%', height: 200, objectFit: 'cover' }}
            onError={(e) => {
              e.target.style.backgroundColor = '#f0f0f0'
              e.target.style.display = 'flex'
              e.target.style.alignItems = 'center'
              e.target.style.justifyContent = 'center'
              e.target.innerHTML = '<span style="color:#999">封面图</span>'
            }}
          />
        }
      >
        <div style={{ marginBottom: 16 }}>
          <h1 style={{ margin: 0 }}>{group.name}</h1>
          <Space style={{ marginTop: 8 }}>
            <Tag>{group.city}</Tag>
            <Tag color="blue">{group.type}</Tag>
            <span style={{ color: '#999' }}>成员数: {group.members || 0}</span>
          </Space>
        </div>
        <p>{group.description || '暂无描述'}</p>
        <Space>
          {group.joined ? (
            <Button danger onClick={handleLeave}>退出群组</Button>
          ) : (
            <Button type="primary" onClick={handleJoin}>加入群组</Button>
          )}
        </Space>
      </Card>

      <Card title="群内帖子" style={{ marginTop: 16 }}>
        {posts.length === 0 ? (
          <Empty description="暂无帖子" />
        ) : (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {posts.map((post) => (
              <Card key={post.id} size="small">
                <div>
                  <strong>{post.title}</strong>
                  <div style={{ marginTop: 8, color: '#666' }}>{post.content}</div>
                </div>
              </Card>
            ))}
          </Space>
        )}
      </Card>
    </div>
  )
}

export default Groups

