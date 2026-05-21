import React, { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Avatar, Dropdown } from 'antd';
import { DashboardOutlined, BellOutlined, LogoutOutlined, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import StudentDashboard from './StudentDashboard';
import StudentNotifications from './StudentNotifications';

const { Sider, Header, Content } = Layout;

const StudentLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { key: '/student', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/student/notifications', icon: <BellOutlined />, label: 'Notifications' },
  ];

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <Layout className="app-layout">
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} trigger={null} width={240} className="app-sider">
        <div className="sider-logo"><h2>{collapsed ? 'ES' : 'Student'}</h2></div>
        <Menu mode="inline" selectedKeys={[location.pathname]} items={menuItems} onClick={({ key }) => navigate(key)} style={{ borderRight: 'none', background: 'transparent' }} />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Button type="text" icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />} onClick={() => setCollapsed(!collapsed)} style={{ color: '#e2e8f0' }} />
          <Dropdown menu={{ items: [{ key: 'logout', icon: <LogoutOutlined />, label: 'Logout', onClick: handleLogout }] }}>
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar style={{ background: '#10b981' }}>{user?.name?.[0] || 'S'}</Avatar>
              <span style={{ color: '#e2e8f0' }}>{user?.name}</span>
            </div>
          </Dropdown>
        </Header>
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<StudentDashboard />} />
            <Route path="/notifications" element={<StudentNotifications />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default StudentLayout;
