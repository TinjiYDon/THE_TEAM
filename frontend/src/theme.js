// WeBank 微众银行主题配置（红白蓝）
export const weBankTheme = {
  token: {
    // 主色调 - WeBank 红色
    colorPrimary: '#E02020', // WeBank 红
    colorSuccess: '#1890ff', // 蓝色
    colorWarning: '#faad14',
    colorError: '#E02020',
    colorInfo: '#1890ff',
    
    // 字体
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
    fontSize: 14,
    
    // 圆角
    borderRadius: 4,
    
    // 间距
    padding: 16,
    colorBgLayout: '#f5f7fa',
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      bodyBg: '#f5f7fa',
      siderBg: '#ffffff',
    },
    Menu: {
      itemColor: '#333333',
      itemHoverColor: '#E02020',
      itemSelectedColor: '#E02020',
      itemSelectedBg: '#fff5f5',
    },
    Button: {
      borderRadius: 4,
    },
    Card: {
      borderRadiusLG: 8,
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    },
  },
}

