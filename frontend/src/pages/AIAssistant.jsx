import React, { useState, useRef, useEffect } from 'react'
import { Card, Input, Button, Space, Avatar, message, Tag } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, ThunderboltOutlined } from '@ant-design/icons'
import api from '../utils/api'

function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '您好！我是您的账单小助手。我可以帮您分析消费、推荐商家、预测趋势等。试试问我："今日消费分析"或"消费趋势分析"',
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const quickActions = [
    { label: '今日消费分析', query: '今日消费分析' },
    { label: '消费趋势分析', query: '消费趋势分析' },
    { label: '好商家推荐', query: '好商家推荐' },
    { label: '消费预警', query: '消费预警' },
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage = { role: 'user', content: inputValue }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      const res = await api.post('/ai/advice/1', { query: inputValue })
      const assistantMessage = {
        role: 'assistant',
        content: res.cards ? JSON.stringify(res.cards, null, 2) : '抱歉，我暂时无法理解您的问题。',
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      message.error('发送失败，请重试')
      setMessages((prev) => [...prev, { role: 'assistant', content: '抱歉，发生了错误。' }])
    } finally {
      setLoading(false)
    }
  }

  const handleQuickAction = (query) => {
    setInputValue(query)
    handleSend()
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24, fontSize: 24, fontWeight: 'bold' }}>AI助手</h1>

      <Card
        title={
          <Space>
            <RobotOutlined style={{ color: '#E02020' }} />
            <span>智能对话助手</span>
          </Space>
        }
        style={{ marginBottom: 16 }}
      >
        <div style={{ 
          height: '500px', 
          overflowY: 'auto', 
          padding: '16px',
          background: '#f5f7fa',
          borderRadius: 8,
          marginBottom: 16
        }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                marginBottom: 16,
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <Space direction="vertical" align={msg.role === 'user' ? 'end' : 'start'}>
                <Avatar
                  icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  style={{
                    background: msg.role === 'user' ? '#1890ff' : '#E02020',
                  }}
                />
                <Card
                  style={{
                    maxWidth: '70%',
                    background: msg.role === 'user' ? '#1890ff' : '#ffffff',
                    color: msg.role === 'user' ? '#ffffff' : '#333',
                  }}
                >
                  {msg.content}
                </Card>
              </Space>
            </div>
          ))}
          {loading && (
            <div style={{ textAlign: 'center', color: '#999' }}>
              <RobotOutlined spin /> 思考中...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Space wrap>
              {quickActions.map((action, idx) => (
                <Button
                  key={idx}
                  icon={<ThunderboltOutlined />}
                  onClick={() => handleQuickAction(action.query)}
                  disabled={loading}
                >
                  {action.label}
                </Button>
              ))}
            </Space>
          </div>

          <Input.Group compact>
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onPressEnter={handleSend}
              placeholder="输入您的问题..."
              style={{ flex: 1 }}
              disabled={loading}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={loading}
            >
              发送
            </Button>
          </Input.Group>
        </Space>
      </Card>
    </div>
  )
}

export default AIAssistant

