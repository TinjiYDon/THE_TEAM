// WeBank 微众银行主题配置（红白蓝）
export const weBankTheme = {
  token: {
    // 主色调 - WeBank 红色
    colorPrimary: '#E02020',
    colorSuccess: '#1D7FFF',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#3C89FF',
    colorPrimaryBg: '#fff5f5',

    // 字体
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
    fontSize: 14,

    // 圆角
    borderRadius: 6,

    // 间距
    padding: 16,
    colorBgLayout: '#f3f5fb',
    colorBgSpotlight: 'linear-gradient(135deg, rgba(224,32,32,0.08) 0%, rgba(50,109,255,0.08) 100%)',
    boxShadowSecondary: '0 6px 16px rgba(24, 39, 75, 0.12)',
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      bodyBg: '#f3f5fb',
      siderBg: '#ffffff',
      headerPadding: '0 24px',
    },
    Menu: {
      itemColor: '#333333',
      itemHoverColor: '#E02020',
      itemSelectedColor: '#E02020',
      itemSelectedBg: '#fff5f5',
      itemBorderRadius: 6,
    },
    Button: {
      borderRadius: 6,
      boxShadow: '0 8px 16px rgba(224,32,32,0.16)',
    },
    Card: {
      borderRadiusLG: 12,
      boxShadow: '0 6px 16px rgba(24,39,75,0.08)',
      headerFontSize: 16,
      headerHeight: 52,
    },
  },
}

export const gradientBg = {
  background: 'linear-gradient(135deg, rgba(224,32,32,0.12) 0%, rgba(50,109,255,0.12) 100%)',
}
