import React, { useState, useEffect } from 'react'
import { Layout, Menu, Avatar, Dropdown, Space, Modal, Form, Input, Button } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  FileTextOutlined,
  BarChartOutlined,
  RobotOutlined,
  GiftOutlined,
  TeamOutlined,
  HeartOutlined,
  UserOutlined,
  LogoutOutlined,
  LoginOutlined
} from '@ant-design/icons'
import api from '../utils/api'

const { Header, Sider, Content } = Layout

const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '账单小助手' },
  { key: '/bills', icon: <FileTextOutlined />, label: '账单管理' },
  { key: '/analysis', icon: <BarChartOutlined />, label: '消费分析' },
  { key: '/ai-assistant', icon: <RobotOutlined />, label: 'AI助手' },
  { key: '/recommendations', icon: <GiftOutlined />, label: '金融产品推荐' },
  { key: '/community', icon: <TeamOutlined />, label: '社区' },
  { key: '/health', icon: <HeartOutlined />, label: '健康消费' },
]


function MainLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [user, setUser] = useState(null)
  const [loginVisible, setLoginVisible] = useState(false)
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    // 尝试获取当前用户信息
    loadCurrentUser()
  }, [])

  const loadCurrentUser = async () => {
    try {
      const res = await api.get('/auth/me')
      if (res.success) {
        setUser(res.user)
      }
    } catch (error) {
      // 未登录或获取失败，显示登录按钮
      setUser(null)
    }
  }

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  const handleUserMenuClick = ({ key }) => {
    if (key === 'login') {
      setLoginVisible(true)
    } else if (key === 'logout') {
      setUser(null)
      setLoginVisible(true)
    } else if (key === 'profile') {
      // 显示个人信息
    }
  }

  const handleLogin = async (values) => {
    try {
      const res = await api.post('/auth/login', values)
      if (res.success) {
        setUser(res.user)
        setLoginVisible(false)
        form.resetFields()
      }
    } catch (error) {
      console.error('登录失败:', error)
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={200}
        style={{
          background: '#ffffff',
          boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
        }}
      >
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          borderBottom: '1px solid #f0f0f0'
        }}>
          {!collapsed ? (
            <span style={{ fontSize: 18, fontWeight: 'bold', color: '#E02020' }}>
              账单小助手
            </span>
          ) : (
            <span style={{ fontSize: 20, color: '#E02020' }}>💰</span>
          )}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ border: 'none', marginTop: 8 }}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          background: '#ffffff', 
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontSize: 18, fontWeight: 'bold', color: '#333' }}>
            智能账单管理系统
          </div>
          {user ? (
            <Dropdown menu={{
              items: [
                { key: 'profile', icon: <UserOutlined />, label: '个人信息' },
                { type: 'divider' },
                { key: 'logout', icon: <LogoutOutlined />, label: '退出登录' },
              ],
              onClick: handleUserMenuClick
            }}>
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <span>{user.username}</span>
              </Space>
            </Dropdown>
          ) : (
            <Button type="primary" icon={<LoginOutlined />} onClick={() => setLoginVisible(true)}>
              登录
            </Button>
          )}

          <Modal
            title="用户登录"
            open={loginVisible}
            onCancel={() => {
              setLoginVisible(false)
              form.resetFields()
            }}
            footer={null}
          >
            <Form
              form={form}
              onFinish={handleLogin}
              layout="vertical"
            >
              <Form.Item
                name="username"
                label="用户名"
                rules={[{ required: true, message: '请输入用户名' }]}
              >
                <Input placeholder="输入用户名 (user1/user2/user3)" />
              </Form.Item>
              <Form.Item
                name="password"
                label="密码"
                rules={[{ required: true, message: '请输入密码' }]}
              >
                <Input.Password placeholder="输入密码 (demo123)" />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" block>
                  登录
                </Button>
              </Form.Item>
              <div style={{ fontSize: 12, color: '#999', textAlign: 'center' }}>
                演示账号：user1/user2/user3，密码：demo123
              </div>
            </Form>
          </Modal>
        </Header>
        <Content style={{ 
          margin: '24px', 
          padding: '24px', 
          background: '#ffffff',
          borderRadius: 8,
          minHeight: 280
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout

