import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Spin } from 'antd';
import {
  TeamOutlined, BankOutlined, ScheduleOutlined, UserSwitchOutlined,
  CheckCircleOutlined, ClockCircleOutlined, AppstoreOutlined, BarChartOutlined,
} from '@ant-design/icons';
import { adminAPI } from '../../api';

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminAPI.dashboardStats()
      .then(res => setStats(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>;

  const cards = [
    { title: 'Total Students', value: stats?.total_students || 0, icon: <TeamOutlined />, cls: 'purple' },
    { title: 'Total Halls', value: stats?.total_halls || 0, icon: <BankOutlined />, cls: 'cyan' },
    { title: 'Total Exams', value: stats?.total_exams || 0, icon: <ScheduleOutlined />, cls: 'green' },
    { title: 'Invigilators', value: stats?.total_invigilators || 0, icon: <UserSwitchOutlined />, cls: 'orange' },
    { title: 'Upcoming Exams', value: stats?.upcoming_exams || 0, icon: <ClockCircleOutlined />, cls: 'blue' },
    { title: 'Active Exams', value: stats?.active_exams || 0, icon: <CheckCircleOutlined />, cls: 'red' },
    { title: 'Completed', value: stats?.completed_exams || 0, icon: <BarChartOutlined />, cls: 'green' },
    { title: 'Seated Students', value: stats?.total_seating_arrangements || 0, icon: <AppstoreOutlined />, cls: 'purple' },
  ];

  return (
    <div className="fade-in-up">
      <div className="page-header"><h2>Admin Dashboard</h2></div>
      <Row gutter={[16, 16]}>
        {cards.map((c, i) => (
          <Col xs={24} sm={12} md={8} lg={6} key={i}>
            <Card className="stat-card" bordered={false}>
              <div className={`stat-icon ${c.cls}`}>{c.icon}</div>
              <div className="stat-value">{c.value}</div>
              <div className="stat-label">{c.title}</div>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default AdminDashboard;
