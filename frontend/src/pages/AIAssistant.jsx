import React, { useState, useRef, useEffect } from 'react'
import { Card, Input, Button, Space, Avatar, message, Tag } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, ThunderboltOutlined } from '@ant-design/icons'
import api from '../utils/api'

function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '您好！我是您的账单小助手。我可以帮您分析消费、推荐商家、预测趋势等。试试问我:"今日消费分析"或"消费趋势分析"',
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

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

  useEffect(() => {
    // 自动聚焦输入框
    inputRef.current?.focus()
  }, [])

  const sendQuery = async (queryText) => {
    if (!queryText.trim()) return

    const userMessage = { role: 'user', content: queryText }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      const res = await api.post('/ai/advice/1', { query: queryText })
      
      // 优先使用人性化回复
      let content = res.humanized || '抱歉，我暂时无法理解您的问题。请试试问我:"今日消费分析"、"消费趋势分析"等。'
      
      // 如果有cards，补充详细信息
      if (res.cards && res.cards.length > 0) {
        const cardsContent = res.cards.map(card => {
          if (card.type === 'summary') {
            return `📊 ${card.title}\n${card.content}`
          } else if (card.type === 'tip') {
            return `💡 ${card.title}\n${card.content}`
          } else if (card.type === 'recommendation') {
            if (card.items && card.items.length > 0) {
              const itemsText = card.items.map((item, idx) => 
                `${idx + 1}. ${item.merchant || item.name} - 访问${item.visits || 0}次，评分${(item.score || 0).toFixed(1)}`
              ).join('\n')
              return `⭐ ${card.title}\n${itemsText}`
            }
            return `⭐ ${card.title}：${card.content || '暂无推荐'}`
          } else if (card.type === 'alert') {
            return `⚠️ ${card.title}\n${card.content}`
          }
          return `${card.title}：${card.content}`
        }).join('\n\n')
        
        // 组合人性化回复和详细信息
        content = content + (cardsContent ? '\n\n' + cardsContent : '')
      }
      
      const assistantMessage = {
        role: 'assistant',
        content: content,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      message.error('发送失败，请重试')
      setMessages((prev) => [...prev, { role: 'assistant', content: '抱歉，发生了错误。' }])
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim()) return
    await sendQuery(inputValue)
  }

  const handleQuickAction = (query) => {
    // 直接发送，避免读取到未更新的 inputValue
    sendQuery(query)
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
              ref={inputRef}
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

