import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Button, Spin, Tag, Divider, Empty } from 'antd';
import { useNavigate } from 'react-router-dom';
import { CalendarOutlined, ClockCircleOutlined, BankOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { invigilatorAPI } from '../../api';

const { Title, Text } = Typography;

const STATUS_COLORS: Record<string, string> = {
  draft: 'gold', published: 'blue', ongoing: 'green', completed: 'purple', cancelled: 'red',
};

const InvigilatorDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    invigilatorAPI.dashboard().then(res => setData(res.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const renderDutyCard = (duty: any) => (
    <Col xs={24} sm={12} md={8} key={duty.id}>
      <Card
        hoverable
        className="stat-card"
        style={{
          borderColor: duty.status === 'completed' ? '#722ed1' : 'var(--primary)',
          opacity: duty.status === 'completed' ? 0.85 : 1,
        }}
        actions={[
          <Button
            type="primary"
            onClick={() => navigate(`/invigilator/duty/${duty.id}`)}
            icon={duty.status === 'completed' ? <CheckCircleOutlined /> : undefined}
          >
            {duty.status === 'completed' ? 'View Details' : 'View Details'}
          </Button>
        ]}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
          <Title level={4} style={{ margin: 0 }}>{duty.subject_name}</Title>
          <Tag color={STATUS_COLORS[duty.status] || 'default'}>{duty.status?.toUpperCase()}</Tag>
        </div>
        <div style={{ marginBottom: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <CalendarOutlined style={{ color: 'var(--text-secondary)' }} />
            <Text>{duty.exam_date}</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <ClockCircleOutlined style={{ color: 'var(--text-secondary)' }} />
            <Text>{duty.start_time} - {duty.end_time}</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <BankOutlined style={{ color: 'var(--text-secondary)' }} />
            <Text strong>Hall: {duty.hall_number}</Text>
          </div>
        </div>
      </Card>
    </Col>
  );

  return (
    <div className="fade-in-up">
      <div className="page-header"><h2>My Exam Duties</h2></div>
      
      {!data?.has_duties ? (
        <Card style={{ textAlign: 'center', padding: 50 }}>
          <Title level={3}>No Exam Duties Assigned</Title>
          <Text type="secondary">You will be notified when duties are assigned to you.</Text>
        </Card>
      ) : (
        <>
          {/* Upcoming / Active Duties */}
          {data.upcoming_duties?.length > 0 && (
            <>
              <Divider orientation="left">
                <Tag color="blue" style={{ fontSize: 14, padding: '4px 12px' }}>
                  Upcoming & Active Duties ({data.upcoming_duties.length})
                </Tag>
              </Divider>
              <Row gutter={[16, 16]}>
                {data.upcoming_duties.map(renderDutyCard)}
              </Row>
            </>
          )}

          {/* Past / Completed Duties */}
          {data.past_duties?.length > 0 && (
            <>
              <Divider orientation="left" style={{ marginTop: 32 }}>
                <Tag color="purple" style={{ fontSize: 14, padding: '4px 12px' }}>
                  Past Duties ({data.past_duties.length})
                </Tag>
              </Divider>
              <Row gutter={[16, 16]}>
                {data.past_duties.map(renderDutyCard)}
              </Row>
            </>
          )}

          {data.upcoming_duties?.length === 0 && data.past_duties?.length === 0 && (
            <Empty description="No duties found" style={{ padding: '60px 0' }} />
          )}
        </>
      )}
    </div>
  );
};

export default InvigilatorDashboard;
