import React, { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Avatar, Dropdown } from 'antd';
import { DashboardOutlined, ScheduleOutlined, LogoutOutlined, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import InvigilatorDashboard from './InvigilatorDashboard';
import DutyDetails from './DutyDetails';

const { Sider, Header, Content } = Layout;

const InvigilatorLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { key: '/invigilator', icon: <DashboardOutlined />, label: 'Dashboard' },
  ];

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <Layout className="app-layout">
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} trigger={null} width={240} className="app-sider">
        <div className="sider-logo"><h2>{collapsed ? 'ES' : 'Invigilator'}</h2></div>
        <Menu mode="inline" selectedKeys={[location.pathname]} items={menuItems} onClick={({ key }) => navigate(key)} style={{ borderRight: 'none', background: 'transparent' }} />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Button type="text" icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />} onClick={() => setCollapsed(!collapsed)} style={{ color: '#e2e8f0' }} />
          <Dropdown menu={{ items: [{ key: 'logout', icon: <LogoutOutlined />, label: 'Logout', onClick: handleLogout }] }}>
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar style={{ background: '#f59e0b' }}>{user?.name?.[0] || 'I'}</Avatar>
              <span style={{ color: '#e2e8f0' }}>{user?.name}</span>
            </div>
          </Dropdown>
        </Header>
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<InvigilatorDashboard />} />
            <Route path="/duty/:id" element={<DutyDetails />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default InvigilatorLayout;
