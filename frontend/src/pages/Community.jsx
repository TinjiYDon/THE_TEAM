import React, { useEffect, useState } from 'react'
import { Card, Button, Space, Avatar, Input, message, Spin, Empty } from 'antd'
import { LikeOutlined, MessageOutlined, UserOutlined, SendOutlined } from '@ant-design/icons'
import api from '../utils/api'
import dayjs from 'dayjs'

function Community() {
  const [loading, setLoading] = useState(false)
  const [posts, setPosts] = useState([])
  const [newPostTitle, setNewPostTitle] = useState('')
  const [newPostContent, setNewPostContent] = useState('')

  useEffect(() => {
    loadPosts()
  }, [])

  const loadPosts = async () => {
    setLoading(true)
    try {
      const res = await api.get('/community/posts')
      setPosts(res.data || [])
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
      await api.post('/community/posts', {
        title: newPostTitle,
        content: newPostContent,
      })
      message.success('发布成功')
      setNewPostTitle('')
      setNewPostContent('')
      loadPosts()
    } catch (error) {
      message.error('发布失败')
    }
  }

  if (loading && posts.length === 0) {
    return <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '50px' }} />
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24, fontSize: 24, fontWeight: 'bold' }}>社区</h1>

      <Card title="发布新帖" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Input
            placeholder="标题"
            value={newPostTitle}
            onChange={(e) => setNewPostTitle(e.target.value)}
          />
          <Input.TextArea
            placeholder="内容"
            rows={4}
            value={newPostContent}
            onChange={(e) => setNewPostContent(e.target.value)}
          />
          <Button type="primary" icon={<SendOutlined />} onClick={handleCreatePost}>
            发布
          </Button>
        </Space>
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

