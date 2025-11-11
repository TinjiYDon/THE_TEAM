import React, { useState, useEffect, useMemo } from 'react'
import { Layout, Menu, Avatar, Dropdown, Space, Modal, Form, Input, Button, Switch, ConfigProvider, theme, Typography } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  FileTextOutlined,
  BarChartOutlined,
  RobotOutlined,
  GiftOutlined,
  TeamOutlined,
  HeartOutlined,
  ExperimentOutlined,
  UserOutlined,
  LogoutOutlined,
  LoginOutlined,
  FireOutlined,
  MessageOutlined,
  AlertOutlined as AlertIcon,
  SettingOutlined as SettingIcon
} from '@ant-design/icons'
import api from '../utils/api'
import { gradientBg } from '../theme'

const { Header, Sider, Content } = Layout
const { Text } = Typography

const menuItems = [
  { key: '/assistant', icon: <DashboardOutlined />, label: '账单小助手' },
  { key: '/bills', icon: <FileTextOutlined />, label: '账单管理' },
  { key: '/ranking', icon: <FireOutlined />, label: '热门榜单' },
  { key: '/community', icon: <TeamOutlined />, label: '社群广场' },
  { key: '/groups', icon: <TeamOutlined />, label: '群组列表' },
  { key: '/ai-assistant', icon: <RobotOutlined />, label: 'AI助手' },
  { key: '/recommendations', icon: <GiftOutlined />, label: '金融产品推荐' },
  { key: '/health', icon: <HeartOutlined />, label: '健康消费' },
  { key: '/feedback', icon: <MessageOutlined />, label: '意见反馈' },
  { key: '/warnings', icon: <AlertIcon />, label: '预警中心' },
  { key: '/warning-settings', icon: <SettingIcon />, label: '预警设置' },
  { key: '/profile', icon: <UserOutlined />, label: '个人中心' },
  { key: '/eval', icon: <ExperimentOutlined />, label: '评测与实验' },
]


function MainLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [user, setUser] = useState(null)
  const [loginVisible, setLoginVisible] = useState(false)
  const [darkMode, setDarkMode] = useState(false)

  // 读取/持久化暗黑模式偏好
  useEffect(() => {
    try {
      const v = localStorage.getItem('pref_dark_mode')
      if (v === '1') setDarkMode(true)
    } catch {}
  }, [])
  useEffect(() => {
    try {
      localStorage.setItem('pref_dark_mode', darkMode ? '1' : '0')
    } catch {}
  }, [darkMode])
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
      navigate('/profile')
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

  const layoutTheme = useMemo(() => ({
    algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      colorBgLayout: darkMode ? '#1a1a1a' : '#f5f7fa',
    },
    components: {
      Layout: {
        headerBg: darkMode ? '#1f1f1f' : '#ffffff',
        bodyBg: darkMode ? '#1a1a1a' : '#f5f7fa',
        siderBg: darkMode ? '#171717' : '#ffffff',
      },
      Menu: {
        itemColor: darkMode ? 'rgba(255,255,255,0.85)' : '#333333',
        itemHoverColor: '#E02020',
        itemSelectedColor: '#E02020',
        itemSelectedBg: darkMode ? 'rgba(224,32,32,0.25)' : '#fff5f5',
      },
    },
  }), [darkMode])

  return (
    <ConfigProvider theme={layoutTheme}>
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={200}
        style={{
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
          background: darkMode ? '#1f1f1f' : '#ffffff', 
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: darkMode ? '0 2px 8px rgba(0,0,0,0.25)' : '0 6px 16px rgba(24,39,75,0.08)'
        }}>
          <Space direction="vertical" size={0}>
            <div style={{ fontSize: 18, fontWeight: 700, color: darkMode ? '#ffffff' : '#1f1f1f' }}>
              智能账单管理系统
            </div>
            <Text style={{ fontSize: 12, color: darkMode ? '#9ca4c1' : '#6b7088' }}>
              AI 助力消费洞察 · 智慧掌控财务健康
            </Text>
          </Space>
          <Space size="large">
            <Space>
              <span style={{ color: '#999' }}>暗黑模式</span>
              <Switch checked={darkMode} onChange={setDarkMode} />
            </Space>
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
          </Space>

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
          background: 'transparent',
          borderRadius: 8,
          minHeight: 280
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
    </ConfigProvider>
  )
}

export default MainLayout

