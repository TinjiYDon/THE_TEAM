import React, { useEffect, useState, useMemo } from 'react'
import { Card, Button, Space, Avatar, Input, message, Spin, Empty, Select, Form, Modal, Tabs, Tag, Alert } from 'antd'
import { LikeOutlined, MessageOutlined, UserOutlined, SendOutlined, SearchOutlined, EyeOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'
import { getCurrentUserId, getCurrentCity, setCurrentCity } from '../utils/session'

const { TabPane } = Tabs

function Community() {
  const [loading, setLoading] = useState(false)
  const [posts, setPosts] = useState([])
  const [activeTab, setActiveTab] = useState('plaza') // plaza | my_groups
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCity, setSelectedCity] = useState(getCurrentCity())
  const [visibilityFilter, setVisibilityFilter] = useState('all') // all | public | same_city
  
  // 发帖相关
  const [postModalVisible, setPostModalVisible] = useState(false)
  const [newPostTitle, setNewPostTitle] = useState('')
  const [newPostContent, setNewPostContent] = useState('')
  const [selectedBillId, setSelectedBillId] = useState(null)
  const [selectedGroupId, setSelectedGroupId] = useState(null)
  const [postVisibility, setPostVisibility] = useState('public')
  const [availableBills, setAvailableBills] = useState([])
  const [availableGroups, setAvailableGroups] = useState([])
  const [myGroups, setMyGroups] = useState([])
  const [form] = Form.useForm()
  
  // 洞察相关
  const [insight, setInsight] = useState(null)
  const [joinModal, setJoinModal] = useState(false)

  const userId = useMemo(() => getCurrentUserId(), [])
  const city = useMemo(() => getCurrentCity(), [])

  useEffect(() => {
    loadPosts()
    loadAvailableBills()
    loadGroups()
    loadMyGroups()
    checkInsight()
  }, [activeTab, searchQuery, selectedCity, visibilityFilter, userId])

  const checkInsight = async () => {
    try {
      const res = await api.get('/insight/dining-bias', { params: { user_id: userId, city: selectedCity } })
      const insightData = res.data?.data || res.data || res
      console.log('🍽️ Insight in Community:', insightData)
      setInsight(insightData)
      if (insightData?.trigger === true) {
        setJoinModal(true)
      }
    } catch (e) {
      console.error('加载洞察失败:', e)
    }
  }

  const loadGroups = async () => {
    try {
      const res = await api.get('/groups', { params: { limit: 100 } })
      const groupsData = res.data?.data || res.data || res || []
      console.log('🏘️ Available groups:', groupsData)
      setAvailableGroups(Array.isArray(groupsData) ? groupsData : [])
    } catch (e) {
      console.error('加载群组列表失败:', e)
      setAvailableGroups([])
    }
  }

  const loadMyGroups = async () => {
    try {
      const res = await api.get('/groups/mine', { params: { user_id: userId } })
      const groupsData = res.data?.data || res.data || res || []
      console.log('👥 My groups:', groupsData)
      setMyGroups(Array.isArray(groupsData) ? groupsData : [])
    } catch (e) {
      console.error('加载我的群组失败:', e)
      setMyGroups([])
    }
  }

  const loadAvailableBills = async () => {
    try {
      const res = await api.get('/bills', { params: { limit: 50, user_id: userId } })
      if (res.success && res.data) {
        setAvailableBills(res.data || [])
      }
    } catch (error) {
      console.error('加载账单列表失败:', error)
    }
  }

  const loadPosts = async () => {
    setLoading(true)
    try {
      const params = {
        user_id: userId,
        scope: activeTab,
        visibility: visibilityFilter,
        city: selectedCity,
        q: searchQuery || undefined,
        limit: 50,
      }
      const res = await api.get('/community/feed', { params })
      const postsData = res.success ? (res.data || []) : []
      setPosts(postsData)
    } catch (error) {
      console.error('加载帖子失败:', error)
      setPosts([])
    } finally {
      setLoading(false)
    }
  }

  const handleLike = async (postId) => {
    try {
      await api.post(`/community/posts/${postId}/like`, null, { params: { user_id: userId } })
      message.success('点赞成功')
      loadPosts()
    } catch (error) {
      message.error('点赞失败')
    }
  }

  const handleCreatePost = async () => {
    if (!newPostTitle.trim() || !newPostContent.trim()) {
      message.warning('请填写标题和内容')
      return
    }

    try {
      const params = {
        user_id: userId,
        visibility: postVisibility,
        group_id: selectedGroupId || undefined,
        attached_bill_id: selectedBillId || undefined,
        city: selectedCity,
      }
      const postData = {
        title: newPostTitle,
        content: newPostContent,
        bill_id: selectedBillId || undefined,
      }
      
      const res = await api.post('/community/posts', postData, { params })
      
      if (res.success !== false) {
        message.success('发布成功！')
        setNewPostTitle('')
        setNewPostContent('')
        setSelectedBillId(null)
        setSelectedGroupId(null)
        setPostVisibility('public')
        form.resetFields()
        setPostModalVisible(false)
        await loadPosts()
      } else {
        message.error(res.message || '发布失败，请重试')
      }
    } catch (error) {
      console.error('发布帖子失败:', error)
      const errorMsg = error.response?.data?.detail || error.message || '发布失败，请检查网络连接和后端服务是否启动'
      message.error(errorMsg)
    }
  }

  const handleJoinGroup = async (groupId) => {
    try {
      await api.post(`/groups/${groupId}/join`, null, { params: { user_id: userId } })
      message.success('已加入群组')
      loadMyGroups()
      loadGroups()
    } catch (e) {
      message.error('加入失败')
    }
  }

  const getVisibilityLabel = (vis) => {
    const map = { public: '公开', same_city: '同城', private: '私密' }
    return map[vis] || '公开'
  }

  const getCityName = (code) => {
    const map = { shanghai: '上海', beijing: '北京', suzhou: '苏州' }
    return map[code] || code
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 'bold' }}>社群广场</h1>
        <Button type="primary" onClick={() => setPostModalVisible(true)} icon={<SendOutlined />}>
          发布帖子
        </Button>
      </div>

      {/* 洞察卡片 */}
      {insight?.trigger && (
        <Alert
          type="info"
          showIcon
          message={`检测到餐饮偏好，建议加入 ${getCityName(selectedCity)} 餐饮群`}
          action={
            <Button size="small" onClick={() => setJoinModal(true)}>
              加入群组
            </Button>
          }
          style={{ marginBottom: 16 }}
        />
      )}

      {/* 搜索和筛选 */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="搜索帖子（关键词）"
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onPressEnter={loadPosts}
            allowClear
          />
          <Select
            style={{ width: 120 }}
            value={selectedCity}
            onChange={(v) => { setSelectedCity(v); setCurrentCity(v); }}
          >
            <Select.Option value="shanghai">上海</Select.Option>
            <Select.Option value="beijing">北京</Select.Option>
            <Select.Option value="suzhou">苏州</Select.Option>
          </Select>
          <Select
            style={{ width: 120 }}
            value={visibilityFilter}
            onChange={setVisibilityFilter}
          >
            <Select.Option value="all">全部可见</Select.Option>
            <Select.Option value="public">公开</Select.Option>
            <Select.Option value="same_city">同城</Select.Option>
          </Select>
          <Button onClick={loadPosts}>刷新</Button>
        </Space>
      </Card>

      {/* 广场/我的社群切换 */}
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="广场" key="plaza">
          {loading && posts.length === 0 ? (
            <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
          ) : posts.length === 0 ? (
            <Empty description="暂无帖子" />
          ) : (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {posts.map((post) => (
                <Card
                  key={post.id}
                  title={
                    <Space>
                      <Avatar icon={<UserOutlined />} />
                      <span>{post.title}</span>
                      <Tag color="blue">{getVisibilityLabel(post.visibility || 'public')}</Tag>
                      {post.group_id && <Tag color="green">群组</Tag>}
                    </Space>
                  }
                  extra={
                    <span style={{ color: '#999', fontSize: 12 }}>
                      {dayjs(post.created_at).format('YYYY-MM-DD HH:mm')}
                    </span>
                  }
                >
                  <p style={{ marginBottom: 16 }}>{post.content}</p>
                  {post.bill_summary && (
                    <Card
                      size="small"
                      style={{ marginBottom: 12, background: '#f5f7fa' }}
                      title="📊 关联账单"
                    >
                      <Space>
                        <span>{post.bill_summary.merchant}</span>
                        <Tag color="red">¥{parseFloat(post.bill_summary.amount).toFixed(2)}</Tag>
                        <Tag>{post.bill_summary.category}</Tag>
                        <span style={{ color: '#999', fontSize: 12 }}>
                          {dayjs(post.bill_summary.consume_time).format('MM-DD HH:mm')}
                        </span>
                      </Space>
                    </Card>
                  )}
                  <Space>
                    <Button
                      icon={<LikeOutlined />}
                      onClick={() => handleLike(post.id)}
                    >
                      {post.likes_count || 0}
                    </Button>
                    <Button icon={<MessageOutlined />}>
                      {post.comments_count || 0}
                    </Button>
                    {post.group_id && !myGroups.find(g => g.id === post.group_id) && (
                      <Button
                        size="small"
                        type="link"
                        onClick={() => handleJoinGroup(post.group_id)}
                      >
                        加入群组
                      </Button>
                    )}
                  </Space>
                </Card>
              ))}
            </Space>
          )}
        </TabPane>
        <TabPane tab="我的社群" key="my_groups">
          {myGroups.length === 0 ? (
            <Empty description="您还没有加入任何群组" />
          ) : (
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              {myGroups.map((group) => (
                <Card
                  key={group.id}
                  title={
                    <Space>
                      <img
                        src={group.cover_url || `/groups/${group.city}-${group.type}.jpg`}
                        alt={group.name}
                        style={{ width: 40, height: 40, borderRadius: 4, objectFit: 'cover' }}
                        onError={(e) => {
                          e.target.style.display = 'none'
                        }}
                      />
                      <span>{group.name}</span>
                      <Tag>{group.city}</Tag>
                      <Tag>{group.type}</Tag>
                    </Space>
                  }
                  extra={
                    <Button size="small" onClick={() => window.location.href = `/groups/${group.id}`}>
                      查看详情
                    </Button>
                  }
                >
                  <p>{group.description || '暂无描述'}</p>
                  <div style={{ color: '#999', fontSize: 12 }}>
                    成员数: {group.members || 0}
                  </div>
                </Card>
              ))}
            </Space>
          )}
        </TabPane>
      </Tabs>

      {/* 发帖弹窗 */}
      <Modal
        title="发布新帖"
        open={postModalVisible}
        onCancel={() => setPostModalVisible(false)}
        onOk={handleCreatePost}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="标题" required>
            <Input
              placeholder="输入帖子标题"
              value={newPostTitle}
              onChange={(e) => setNewPostTitle(e.target.value)}
            />
          </Form.Item>
          <Form.Item label="内容" required>
            <Input.TextArea
              placeholder="输入帖子内容"
              rows={4}
              value={newPostContent}
              onChange={(e) => setNewPostContent(e.target.value)}
            />
          </Form.Item>
          <Form.Item label="可见范围">
            <Select value={postVisibility} onChange={setPostVisibility}>
              <Select.Option value="public">公开（所有人可见）</Select.Option>
              <Select.Option value="same_city">同城（仅同城用户可见）</Select.Option>
              <Select.Option value="private">私密（仅自己可见）</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item label="发布到群组（可选）">
            <Select
              placeholder="选择群组"
              allowClear
              value={selectedGroupId}
              onChange={setSelectedGroupId}
            >
              {myGroups.map(g => (
                <Select.Option key={g.id} value={g.id}>{g.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item label="关联账单（可选）">
            <Select
              placeholder="选择要关联的账单数据"
              allowClear
              value={selectedBillId}
              onChange={setSelectedBillId}
              showSearch
              filterOption={(input, option) =>
                option?.label?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {availableBills.map(bill => (
                <Select.Option
                  key={bill.id}
                  value={bill.id}
                  label={`${bill.merchant} - ¥${parseFloat(bill.amount).toFixed(2)} - ${dayjs(bill.consume_time).format('MM-DD HH:mm')}`}
                >
                  {bill.merchant} - ¥{parseFloat(bill.amount).toFixed(2)} - {dayjs(bill.consume_time).format('MM-DD HH:mm')}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 加入群组弹窗 */}
      <Modal
        open={joinModal}
        title={`加入${getCityName(selectedCity)}餐饮群？`}
        onCancel={() => setJoinModal(false)}
        footer={[
          <Button key="later" onClick={() => setJoinModal(false)}>稍后提醒</Button>,
          <Button key="no" onClick={() => setJoinModal(false)}>暂不加入</Button>,
          <Button key="ok" type="primary" onClick={async () => {
            try {
              const list = await api.get('/groups', { params: { city: getCityName(selectedCity) } })
              const groupsData = list.data?.data || list.data || list || []
              console.log('🔍 Available groups for joining:', groupsData)
              const target = groupsData.find?.(g => (g.name || '').includes('餐饮'))
              console.log('🎯 Target group:', target)
              if (target?.id) {
                await api.post(`/groups/${target.id}/join`, null, { params: { user_id: userId } })
                message.success('已加入群组')
                await loadMyGroups()
              } else {
                message.warning('未找到对应的餐饮群')
              }
            } catch (e) {
              console.error('加入群组失败:', e)
              message.error('加入失败')
            }
            setJoinModal(false)
          }}>加入</Button>
        ]}
      >
        <div style={{ marginBottom: 12 }}>是否记住当前城市选择？</div>
        <Space>
          <Button onClick={() => { setCurrentCity(selectedCity); message.success('已记住城市选择'); }}>记住当前城市</Button>
        </Space>
      </Modal>
    </div>
  )
}

export default Community
