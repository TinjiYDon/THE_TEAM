import React from 'react'
import { Card, Row, Col, Tabs } from 'antd'
import { Column, Line, Pie, Radar } from '@ant-design/charts'

function Analysis() {
  const categoryData = [
    { category: '餐饮', amount: 3500 },
    { category: '交通', amount: 1200 },
    { category: '购物', amount: 4500 },
    { category: '娱乐', amount: 800 },
    { category: '医疗', amount: 500 },
  ]

  const trendData = [
    { month: '1月', amount: 3200 },
    { month: '2月', amount: 3500 },
    { month: '3月', amount: 3800 },
    { month: '4月', amount: 4200 },
    { month: '5月', amount: 4500 },
    { month: '6月', amount: 4800 },
  ]

  const columnConfig = {
    data: categoryData,
    xField: 'category',
    yField: 'amount',
    color: '#E02020',
  }

  const lineConfig = {
    data: trendData,
    xField: 'month',
    yField: 'amount',
    smooth: true,
    color: '#1890ff',
  }

  const pieConfig = {
    data: categoryData,
    angleField: 'amount',
    colorField: 'category',
    radius: 0.8,
    label: { type: 'outer' },
  }

  const radarConfig = {
    data: [
      { item: '餐饮', value: 70 },
      { item: '交通', value: 40 },
      { item: '购物', value: 85 },
      { item: '娱乐', value: 30 },
      { item: '医疗', value: 20 },
    ],
    xField: 'item',
    yField: 'value',
    area: {},
    point: { size: 5 },
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24, fontSize: 24, fontWeight: 'bold' }}>消费分析</h1>
      
      <Tabs
        items={[
          {
            key: 'category',
            label: '分类分析',
            children: (
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={14}>
                  <Card title="分类消费柱状图" style={{ height: 400 }}>
                    <Column {...columnConfig} />
                  </Card>
                </Col>
                <Col xs={24} lg={10}>
                  <Card title="分类占比" style={{ height: 400 }}>
                    <Pie {...pieConfig} />
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: 'trend',
            label: '趋势分析',
            children: (
              <Card title="消费趋势图" style={{ height: 500 }}>
                <Line {...lineConfig} />
              </Card>
            ),
          },
          {
            key: 'radar',
            label: '消费雷达图',
            children: (
              <Card title="消费分布雷达图" style={{ height: 500 }}>
                <Radar {...radarConfig} />
              </Card>
            ),
          },
        ]}
      />
    </div>
  )
}

export default Analysis

