import React, { useEffect, useState } from 'react'
import { Card, Button, Space, Avatar, Input, message, Spin, Empty, Select, Form } from 'antd'
import { LikeOutlined, MessageOutlined, UserOutlined, SendOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'

function Community() {
  const [loading, setLoading] = useState(false)
  const [posts, setPosts] = useState([])
  const [newPostTitle, setNewPostTitle] = useState('')
  const [newPostContent, setNewPostContent] = useState('')
  const [selectedBillId, setSelectedBillId] = useState(null)
  const [availableBills, setAvailableBills] = useState([])
  const [form] = Form.useForm()

  useEffect(() => {
    loadPosts()
    loadAvailableBills()
  }, [])
  
  const loadAvailableBills = async () => {
    try {
      const res = await api.get('/bills', { params: { limit: 50, user_id: 1 } })
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
      const res = await api.get('/community/posts')
      // API 返回格式: { success: true, data: [...] }
      const postsData = res.success ? (res.data || []) : []
      setPosts(postsData)
    } catch (error) {
      console.error('加载帖子失败:', error)
      // 模拟数据
      setPosts([
        {
          id: 1,
          user_id: 1,
          title: '这个月餐饮支出有点多',
          content: '最近发现餐饮支出明显增加，大家有什么建议吗？',
          likes_count: 5,
          comments_count: 3,
          created_at: new Date().toISOString(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleLike = async (postId) => {
    try {
      await api.post(`/community/posts/${postId}/like`)
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
      const postData = {
        title: newPostTitle,
        content: newPostContent,
      }
      
      // 如果选择了账单，添加到请求中
      if (selectedBillId) {
        postData.bill_id = selectedBillId
      }
      
      const res = await api.post('/community/posts', postData)
      
      if (res.success !== false) {
        message.success('发布成功！')
        setNewPostTitle('')
        setNewPostContent('')
        setSelectedBillId(null)
        form.resetFields()
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

  if (loading && posts.length === 0) {
    return <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24, fontSize: 24, fontWeight: 'bold' }}>社区</h1>

      <Card title="发布新帖" style={{ marginBottom: 16 }}>
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
            <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
              选择账单后，帖子会关联该消费记录，防止虚假发帖
            </div>
          </Form.Item>
          <Form.Item>
            <Button type="primary" icon={<SendOutlined />} onClick={handleCreatePost} block>
              发布帖子
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {posts.length === 0 ? (
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
                </Space>
              }
              extra={
                <span style={{ color: '#999', fontSize: 12 }}>
                  {dayjs(post.created_at).format('YYYY-MM-DD HH:mm')}
                </span>
              }
            >
              <p style={{ marginBottom: 16 }}>{post.content}</p>
              {post.bill_id && (
                <div style={{ marginBottom: 12, padding: 8, background: '#f5f7fa', borderRadius: 4, fontSize: 12 }}>
                  📊 关联账单ID: {post.bill_id} (已绑定消费数据)
                </div>
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
              </Space>
            </Card>
          ))}
        </Space>
      )}
    </div>
  )
}

export default Community

