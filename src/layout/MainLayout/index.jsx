import React from 'react';
import { Outlet } from 'react-router-dom';
import { Layout } from 'antd';

const { Header, Sider, Content } = Layout;

const MainLayout = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider>Sidebar</Sider>
      <Layout>
        <Header>Header</Header>
        <Content style={{ margin: '24px 16px', padding: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
