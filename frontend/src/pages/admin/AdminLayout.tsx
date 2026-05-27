import React, { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Avatar, Dropdown } from 'antd';
import {
  DashboardOutlined, TeamOutlined, BookOutlined, BankOutlined,
  ScheduleOutlined, AppstoreOutlined, UserSwitchOutlined,
  AuditOutlined, LogoutOutlined, MenuFoldOutlined, MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import AdminDashboard from './AdminDashboard';
import StudentManagement from './StudentManagement';
import SubjectManagement from './SubjectManagement';
import HallManagement from './HallManagement';
import ExamManagement from './ExamManagement';
import SeatingArrangement from './SeatingArrangement';
import InvigilatorManagement from './InvigilatorManagement';

import AuditLogsPage from './AuditLogsPage';

const { Sider, Header, Content } = Layout;

const AdminLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { key: '/admin', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/admin/students', icon: <TeamOutlined />, label: 'Students' },
    { key: '/admin/subjects', icon: <BookOutlined />, label: 'Subjects' },
    { key: '/admin/halls', icon: <BankOutlined />, label: 'Halls' },
    { key: '/admin/exams', icon: <ScheduleOutlined />, label: 'Exams' },
    { key: '/admin/seating', icon: <AppstoreOutlined />, label: 'Seating' },
    { key: '/admin/invigilators', icon: <UserSwitchOutlined />, label: 'Invigilators' },

    { key: '/admin/audit-logs', icon: <AuditOutlined />, label: 'Audit Logs' },
  ];

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <Layout className="app-layout">
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}
             trigger={null} width={240} className="app-sider">
        <div className="sider-logo">
          <h2>{collapsed ? 'ES' : 'Exam Seating'}</h2>
        </div>
        <Menu
          mode="inline" selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 'none', background: 'transparent' }}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Button type="text" icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                  onClick={() => setCollapsed(!collapsed)} style={{ color: '#e2e8f0' }} />
          <Dropdown menu={{ items: [
            { key: 'logout', icon: <LogoutOutlined />, label: 'Logout', onClick: handleLogout },
          ] }}>
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar style={{ background: 'linear-gradient(135deg, #6366f1, #06b6d4)' }}>
                {user?.name?.[0] || 'A'}
              </Avatar>
              <span style={{ color: '#e2e8f0' }}>{user?.name}</span>
            </div>
          </Dropdown>
        </Header>
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<AdminDashboard />} />
            <Route path="/students" element={<StudentManagement />} />
            <Route path="/subjects" element={<SubjectManagement />} />
            <Route path="/halls" element={<HallManagement />} />
            <Route path="/exams" element={<ExamManagement />} />
            <Route path="/seating" element={<SeatingArrangement />} />
            <Route path="/invigilators" element={<InvigilatorManagement />} />

            <Route path="/audit-logs" element={<AuditLogsPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;
